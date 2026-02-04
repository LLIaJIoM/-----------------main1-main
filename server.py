import os
import json
import urllib.parse
import urllib.request
import ssl
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
try:
    with open(os.path.join(ROOT_DIR, "config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)
        BOT_TOKEN = BOT_TOKEN or str(cfg.get("TELEGRAM_BOT_TOKEN") or cfg.get("bot_token") or "")
        CHAT_ID = CHAT_ID or str(cfg.get("TELEGRAM_CHAT_ID") or cfg.get("chat_id") or "")
except Exception:
    pass

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def normalize_phone(raw):
    digits = "".join(ch for ch in (raw or "") if ch.isdigit())
    if not digits:
        return None
    if digits[0] == "8":
        digits = "7" + digits[1:]
    if len(digits) == 11 and digits[0] == "7":
        return "+" + digits
    return None

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
        phone_norm = normalize_phone(phone)
        if not name or not phone:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "missing_fields"}).encode("utf-8"))
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
        if BOT_TOKEN and CHAT_ID:
            try:
                text = (
                    f"<b>Новая заявка</b>\n"
                    f"Имя: {esc(name)}\n"
                    f"Телефон: {esc(phone_norm)}\n"
                    f"Комментарий: {esc(comment)}\n"
                    f"Источник: Сайт\n"
                    f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                params = urllib.parse.urlencode({
                    "chat_id": CHAT_ID,
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
                        info = {"certifi": True}
                except ssl.SSLError as _e:
                    ctx2 = ssl._create_unverified_context()
                    with urllib.request.urlopen(req, timeout=10, context=ctx2) as resp:
                        payload = resp.read()
                    info = {"tls_unverified": True}
                res = json.loads(payload.decode("utf-8"))
                ok = bool(res.get("ok"))
                if not ok:
                    err = res.get("description") or "telegram_error"
                    info = res
            except Exception as e:
                err = str(e)
        else:
            try:
                rec = {
                    "name": name,
                    "phone": phone_norm,
                    "comment": comment,
                    "page": page,
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
