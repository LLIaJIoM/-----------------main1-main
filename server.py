import os
import json
import urllib.parse
import urllib.request
import ssl
import re
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
try:
    import certifi
    CERT_PATH = certifi.where()
except Exception:
    certifi = None
    CERT_PATH = None
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime
from pages import get_page

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CHAT_IDS = None
env_chat_ids = os.environ.get("TELEGRAM_CHAT_IDS")
if env_chat_ids:
    try:
        # Try parsing as JSON first
        CHAT_IDS = json.loads(env_chat_ids)
        if not isinstance(CHAT_IDS, list):
             CHAT_IDS = None
    except Exception:
        pass
    # If not JSON or failed, try comma-separated
    if not CHAT_IDS:
        CHAT_IDS = [x.strip() for x in env_chat_ids.split(",") if x.strip()]

REVIEWS_TOKEN = os.environ.get("REVIEWS_TOKEN")

try:
    with open(os.path.join(ROOT_DIR, "config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)
        BOT_TOKEN = BOT_TOKEN or str(cfg.get("TELEGRAM_BOT_TOKEN") or cfg.get("bot_token") or "")
        CHAT_ID = CHAT_ID or str(cfg.get("TELEGRAM_CHAT_ID") or cfg.get("chat_id") or "")
        ids = cfg.get("TELEGRAM_CHAT_IDS") or cfg.get("chat_ids") or []
        if isinstance(ids, list):
            CHAT_IDS = [str(x) for x in ids if str(x)]
        REVIEWS_TOKEN = REVIEWS_TOKEN or str(cfg.get("REVIEWS_TOKEN") or cfg.get("reviews_token") or "")
except Exception:
    pass

REVIEWS_FILE = os.path.join(ROOT_DIR, "assets", "reviews.json")
MAX_REVIEWS = 6

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _country_display(phone_norm, phone_iso2, phone_country, phone_dial_code):
    ru_names = {
        "ru": "Россия", "kz": "Казахстан", "by": "Беларусь", "ua": "Украина",
        "us": "США", "gb": "Великобритания", "de": "Германия", "fr": "Франция",
        "es": "Испания", "it": "Италия", "cn": "Китай", "tr": "Турция",
        "in": "Индия", "jp": "Япония", "pl": "Польша", "nl": "Нидерланды",
        "cz": "Чехия", "se": "Швеция", "no": "Норвегия", "fi": "Финляндия",
        "ee": "Эстония", "gp": "Гваделупа", "mf": "Сен-Мартен", "bl": "Сен-Бартелеми"
    }
    iso2 = (phone_iso2 or "").lower()
    if iso2 in ru_names:
        return ru_names[iso2]
    if phone_country:
        return phone_country
    dial_map = {
        "358": "Финляндия", "372": "Эстония", "420": "Чехия",
        "49": "Германия", "44": "Великобритания", "33": "Франция",
        "39": "Италия", "34": "Испания", "86": "Китай", "90": "Турция",
        "91": "Индия", "81": "Япония", "48": "Польша", "31": "Нидерланды",
        "46": "Швеция", "47": "Норвегия", "590": "Гваделупа", "1": "США", "7": "Россия"
    }
    code = (phone_dial_code or "").strip()
    if not code and phone_norm.startswith("+"):
        digits = "".join(ch for ch in phone_norm if ch.isdigit())
        for k in sorted(dial_map.keys(), key=lambda x: -len(x)):
            if digits.startswith(k):
                code = k
                break
    return dial_map.get(code, "")
def normalize_phone(raw):
    # Allow international numbers
    s = (raw or "").strip()
    cleaned = "".join(ch for ch in s if ch.isdigit() or ch == '+')
    if not cleaned:
        return None
    
    # If it starts with 8 and is 11 digits (typical Russian format without +), convert to +7
    digits = "".join(ch for ch in cleaned if ch.isdigit())
    if len(digits) == 11 and digits.startswith("8") and not cleaned.startswith("+"):
        return "+7" + digits[1:]
    
    # If it's a valid length for international number (approx 7-15 digits)
    if len(digits) < 7 or len(digits) > 15:
        return None
        
    if not cleaned.startswith("+"):
        return "+" + digits
        
    return cleaned

def _load_reviews():
    """Load reviews from assets/reviews.json, return list."""
    try:
        with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def _save_reviews(reviews):
    """Save reviews list to assets/reviews.json."""
    with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        full = super().translate_path(path)
        return full
    def do_GET(self):
        if self.path == "/api/reviews":
            payload = _load_reviews()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            return

        # Parse URL path (strip query string)
        url_path = self.path.split("?")[0].split("#")[0]

        # Try dynamic page routing
        html, status = get_page(url_path)
        if html is not None:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        # Fall through to static file serving for assets, etc.
        return super().do_GET()

    def _handle_reviews(self, data):
        """Handle /api/reviews/add and /api/reviews/set endpoints."""
        # ── Token validation ──
        token = str(data.get("token", "")).strip()
        if not REVIEWS_TOKEN or token != REVIEWS_TOKEN:
            self.send_response(403)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "forbidden"}).encode("utf-8"))
            return

        try:
            if self.path == "/api/reviews/add":
                # ── Add single review ──
                review = data.get("review")
                if not review or not isinstance(review, dict):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "missing_review"}).encode("utf-8"))
                    return

                name = str(review.get("name", "")).strip()
                text = str(review.get("text", "")).strip()
                rating = review.get("rating", 5)
                date = str(review.get("date", "")).strip()
                source = str(review.get("source", "Avito")).strip() or "Avito"

                if not name or not text:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "name_and_text_required"}).encode("utf-8"))
                    return

                try:
                    rating = int(rating)
                    rating = max(1, min(5, rating))
                except (ValueError, TypeError):
                    rating = 5

                if not date:
                    date = datetime.now().strftime("%d %B").lstrip("0")

                new_review = {
                    "name": name,
                    "rating": rating,
                    "text": text,
                    "date": date,
                    "source": source
                }

                reviews = _load_reviews()
                reviews.insert(0, new_review)  # Newest first
                reviews = reviews[:MAX_REVIEWS]  # Keep only 6
                _save_reviews(reviews)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "total": len(reviews),
                    "reviews": reviews
                }, ensure_ascii=False).encode("utf-8"))
                return

            elif self.path == "/api/reviews/set":
                # ── Replace all reviews ──
                reviews_data = data.get("reviews")
                if not reviews_data or not isinstance(reviews_data, list):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "missing_reviews_array"}).encode("utf-8"))
                    return

                cleaned = []
                for r in reviews_data[:MAX_REVIEWS]:
                    if not isinstance(r, dict):
                        continue
                    name = str(r.get("name", "")).strip()
                    text = str(r.get("text", "")).strip()
                    if not name or not text:
                        continue
                    try:
                        rating = int(r.get("rating", 5))
                        rating = max(1, min(5, rating))
                    except (ValueError, TypeError):
                        rating = 5
                    cleaned.append({
                        "name": name,
                        "rating": rating,
                        "text": text,
                        "date": str(r.get("date", "")).strip(),
                        "source": str(r.get("source", "Avito")).strip() or "Avito"
                    })

                if not cleaned:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "no_valid_reviews"}).encode("utf-8"))
                    return

                _save_reviews(cleaned)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "total": len(cleaned),
                    "reviews": cleaned
                }, ensure_ascii=False).encode("utf-8"))
                return

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return

    def do_POST(self):
        allowed = ("/api/telegram", "/api/phone-interest", "/api/reviews/add", "/api/reviews/set")
        if self.path not in allowed:
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not_found"}).encode("utf-8"))
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}

        # ─── Управление отзывами ───
        if self.path in ("/api/reviews/add", "/api/reviews/set"):
            return self._handle_reviews(data)

        if self.path == "/api/phone-interest":
            page = str(data.get("page", "")).strip()
            phone = str(data.get("phone", "")).strip()
            source = str(data.get("source", "Сайт")).strip() or "Сайт"
            msg_type = str(data.get("type", "phone")).strip()
            ok = False
            err = None
            info = None
            recipients = []
            if CHAT_ID:
                recipients.append(CHAT_ID)
            if isinstance(CHAT_IDS, list) and CHAT_IDS:
                for x in CHAT_IDS:
                    if x:
                        recipients.append(x)
            dedup = []
            seen = set()
            for x in recipients:
                if x not in seen:
                    dedup.append(x)
                    seen.add(x)
            recipients = dedup
            if BOT_TOKEN and recipients:
                try:
                    now = datetime.now()
                    if msg_type == 'whatsapp':
                        parts = [
                            f"💬 <b>Клик по WhatsApp!</b>\n",
                            f"📄 Страница: {esc(page) if page else 'Не указана'}\n",
                            f"🕐 Время: {now.strftime('%d.%m.%Y')}, {now.strftime('%H:%M:%S')}\n",
                            f"📍 Источник: {esc(source)}"
                        ]
                    elif msg_type == 'telegram':
                        parts = [
                            f"✈️ <b>Клик по Telegram!</b>\n",
                            f"📄 Страница: {esc(page) if page else 'Не указана'}\n",
                            f"🕐 Время: {now.strftime('%d.%m.%Y')}, {now.strftime('%H:%M:%S')}\n",
                            f"📍 Источник: {esc(source)}"
                        ]
                    else:
                        clean_phone = phone.replace('tel:', '') if phone else ''
                        parts = [
                            f"📞 <b>Интерес к номеру телефона!</b>\n",
                            f"📱 Телефон: {esc(clean_phone) if clean_phone else 'Не указан'}\n",
                            f"📄 Страница: {esc(page) if page else 'Не указана'}\n",
                            f"🕐 Время: {now.strftime('%d.%m.%Y')}, {now.strftime('%H:%M:%S')}\n",
                            f"📍 Источник: {esc(source)}"
                        ]
                    text = "".join(parts)
                    success = []
                    last_err = None
                    last_info = None
                    for cid in recipients:
                        params = urllib.parse.urlencode({
                            "chat_id": cid,
                            "text": text,
                            "parse_mode": "HTML"
                        }).encode("utf-8")
                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        req = urllib.request.Request(url, data=params, method="POST")
                        try:
                            if CERT_PATH:
                                ctx = ssl.create_default_context(cafile=CERT_PATH)
                            else:
                                ctx = ssl.create_default_context()
                            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                                payload = resp.read()
                            if CERT_PATH:
                                last_info = {"certifi": True}
                        except ssl.SSLError:
                            ctx2 = ssl._create_unverified_context()
                            with urllib.request.urlopen(req, timeout=10, context=ctx2) as resp:
                                payload = resp.read()
                            last_info = {"tls_unverified": True}
                        res = json.loads(payload.decode("utf-8"))
                        if bool(res.get("ok")):
                            success.append(cid)
                        else:
                            last_err = res.get("description") or "telegram_error"
                            last_info = res
                    ok = len(success) > 0
                    err = None if ok else last_err
                    info = {"sent_to": success} if ok else last_info
                except Exception as e:
                    err = str(e)
            else:
                try:
                    rec = {
                        "event": "phone_interest",
                        "phone": phone,
                        "page": page,
                        "source": source,
                        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    p = os.path.join(ROOT_DIR, "requests.log")
                    with open(p, "a", encoding="utf-8") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    ok = True
                    info = {"stored": "requests.log"}
                except Exception as e:
                    err = str(e) or "env_missing"
            if not ok:
                print(f"[telegram] send failed: {err}")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": ok, "error": err, "info": info}).encode("utf-8"))
            return
        name = str(data.get("name", "")).strip()
        phone = str(data.get("phone", "")).strip()
        comment = str(data.get("comment", "")).strip()
        page = str(data.get("page", "")).strip()
        phone_country = str(data.get("phone_country", "")).strip()
        phone_iso2 = str(data.get("phone_iso2", "")).strip()
        phone_dial_code = str(data.get("phone_dial_code", "")).strip()
        source = str(data.get("source", "Сайт")).strip() or "Сайт"
        phone_norm = normalize_phone(phone)
        if not name or not phone:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "missing_fields"}).encode("utf-8"))
            return
        if len(name) > 50:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "name_too_long"}).encode("utf-8"))
            return
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-]+$', name):
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "invalid_name_chars"}).encode("utf-8"))
            return
        if len(comment) > 1000:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "comment_too_long"}).encode("utf-8"))
            return
        if not phone_norm:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "invalid_phone"}).encode("utf-8"))
            return
        ok = False
        err = None
        info = None
        recipients = []
        if CHAT_ID:
            recipients.append(CHAT_ID)
        if isinstance(CHAT_IDS, list) and CHAT_IDS:
            for x in CHAT_IDS:
                if x:
                    recipients.append(x)
        dedup = []
        seen = set()
        for x in recipients:
            if x not in seen:
                dedup.append(x)
                seen.add(x)
        recipients = dedup
        if BOT_TOKEN and recipients:
            try:
                country_display = _country_display(phone_norm, phone_iso2, phone_country, phone_dial_code)
                now = datetime.now()
                parts = [
                    f"🔔 <b>Новая заявка с сайта!</b>\n",
                    f"👤 Имя: {esc(name)}\n",
                    f"📞 Телефон: {esc(phone_norm)}\n",
                ]
                if country_display:
                    parts.append(f"🌍 Страна: {esc(country_display)}\n")
                parts.extend([
                    f"📝 Комментарий: {esc(comment)}\n",
                    f"🕐 Время: {now.strftime('%d.%m.%Y')}, {now.strftime('%H:%M:%S')}\n",
                    f"📍 Источник: {esc(source)}"
                ])
                text = "".join(parts)
                success = []
                last_err = None
                last_info = None
                for cid in recipients:
                    params = urllib.parse.urlencode({
                        "chat_id": cid,
                        "text": text,
                        "parse_mode": "HTML"
                    }).encode("utf-8")
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    req = urllib.request.Request(url, data=params, method="POST")
                    try:
                        if CERT_PATH:
                            ctx = ssl.create_default_context(cafile=CERT_PATH)
                        else:
                            ctx = ssl.create_default_context()
                        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                            payload = resp.read()
                        if CERT_PATH:
                            last_info = {"certifi": True}
                    except ssl.SSLError as _e:
                        ctx2 = ssl._create_unverified_context()
                        with urllib.request.urlopen(req, timeout=10, context=ctx2) as resp:
                            payload = resp.read()
                        last_info = {"tls_unverified": True}
                    res = json.loads(payload.decode("utf-8"))
                    if bool(res.get("ok")):
                        success.append(cid)
                    else:
                        last_err = res.get("description") or "telegram_error"
                        last_info = res
                ok = len(success) > 0
                err = None if ok else last_err
                info = {"sent_to": success} if ok else last_info
            except Exception as e:
                err = str(e)
        else:
            try:
                rec = {
                    "name": name,
                    "phone": phone_norm,
                    "comment": comment,
                    "page": page,
                    "phone_country": phone_country,
                    "phone_iso2": phone_iso2,
                    "phone_dial_code": phone_dial_code,
                    "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                p = os.path.join(ROOT_DIR, "requests.log")
                with open(p, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                ok = True
                info = {"stored": "requests.log"}
            except Exception as e:
                err = str(e) or "env_missing"
        if not ok:
            print(f"[telegram] send failed: {err}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": ok, "error": err, "info": info}).encode("utf-8"))

def run(addr="0.0.0.0", port=8000):
    os.chdir(ROOT_DIR)
    server = HTTPServer((addr, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    addr = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    run(addr, port)
