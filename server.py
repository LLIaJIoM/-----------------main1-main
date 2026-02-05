import os
import json
import urllib.parse
import urllib.request
import ssl
import re
try:
    import certifi
    CERT_PATH = certifi.where()
except Exception:
    certifi = None
    CERT_PATH = None
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime

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

try:
    with open(os.path.join(ROOT_DIR, "config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)
        BOT_TOKEN = BOT_TOKEN or str(cfg.get("TELEGRAM_BOT_TOKEN") or cfg.get("bot_token") or "")
        CHAT_ID = CHAT_ID or str(cfg.get("TELEGRAM_CHAT_ID") or cfg.get("chat_id") or "")
        ids = cfg.get("TELEGRAM_CHAT_IDS") or cfg.get("chat_ids") or []
        if isinstance(ids, list):
            CHAT_IDS = [str(x) for x in ids if str(x)]
except Exception:
    pass

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

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        full = super().translate_path(path)
        return full

    def do_POST(self):
        if self.path != "/api/telegram":
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
        name = str(data.get("name", "")).strip()
        phone = str(data.get("phone", "")).strip()
        comment = str(data.get("comment", "")).strip()
        page = str(data.get("page", "")).strip()
        phone_country = str(data.get("phone_country", "")).strip()
        phone_iso2 = str(data.get("phone_iso2", "")).strip()
        phone_dial_code = str(data.get("phone_dial_code", "")).strip()
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
                parts = [
                    f"<b>Новая заявка</b>\n",
                    f"Имя: {esc(name)}\n",
                    f"Телефон: {esc(phone_norm)}\n",
                ]
                parts.append(f"Страна: {esc(country_display) if country_display else 'Не указана'}\n")
                now = datetime.now()
                parts.extend([
                    f"Комментарий: {esc(comment)}\n",
                    f"Источник: Сайт\n",
                    f"Дата: {now.strftime('%d.%m.%Y')}\n",
                    f"Время: {now.strftime('%H:%M:%S')}"
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
                p = os.path.join(ROOT_DIR, "assets", "requests.log")
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                ok = True
                info = {"stored": "assets/requests.log"}
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
