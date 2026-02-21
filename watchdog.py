import os
import sys
import time
import json
import signal
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_IDS_STR = os.environ.get("TELEGRAM_CHAT_IDS", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CHAT_IDS = []
if CHAT_IDS_STR:
    try:
        CHAT_IDS = json.loads(CHAT_IDS_STR)
    except:
        CHAT_IDS = [x.strip() for x in CHAT_IDS_STR.split(",") if x.strip()]
if CHAT_ID and CHAT_ID not in CHAT_IDS:
    CHAT_IDS.append(CHAT_ID)

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
CHECK_INTERVAL = int(os.environ.get("WATCHDOG_INTERVAL", "60"))
MAX_RESTART_ATTEMPTS = int(os.environ.get("WATCHDOG_MAX_RESTARTS", "3"))
RESTART_COOLDOWN = int(os.environ.get("WATCHDOG_COOLDOWN", "300"))

server_process = None
restart_attempts = 0
last_restart_time = 0
running = True


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [watchdog] {msg}", flush=True)


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_IDS:
        log("Cannot send Telegram: missing token or chat IDs")
        return False
    
    success = False
    for cid in CHAT_IDS:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = json.dumps({
                "chat_id": cid,
                "text": message,
                "parse_mode": "HTML"
            }).encode("utf-8")
            req = urllib.request.Request(
                url, 
                data=data, 
                method="POST",
                headers={"Content-Type": "application/json"}
            )
            import ssl
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("ok"):
                    success = True
                    log(f"Telegram notification sent to {cid}")
        except Exception as e:
            log(f"Telegram error for {cid}: {e}")
    
    return success


def check_server():
    try:
        url = f"http://{HOST}:{PORT}/"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return True
    except urllib.error.HTTPError as e:
        if e.code in (200, 301, 302, 304):
            return True
        log(f"Server returned HTTP {e.code}")
    except Exception as e:
        log(f"Server check failed: {e}")
    return False


def start_server():
    global server_process
    try:
        if server_process and server_process.poll() is None:
            log("Server already running, stopping first...")
            stop_server()
            time.sleep(2)
        
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(__file__), "server.py")
        
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        server_process = subprocess.Popen(
            [python_exe, script_path],
            env=env,
            cwd=os.path.dirname(__file__)
        )
        log(f"Server started (PID: {server_process.pid})")
        time.sleep(3)
        return server_process.poll() is None
    except Exception as e:
        log(f"Failed to start server: {e}")
        return False


def stop_server():
    global server_process
    if server_process:
        try:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait(timeout=5)
            log("Server stopped")
        except Exception as e:
            log(f"Error stopping server: {e}")
        server_process = None


def restart_server():
    global restart_attempts, last_restart_time
    
    now = time.time()
    if now - last_restart_time < RESTART_COOLDOWN:
        wait_time = int(RESTART_COOLDOWN - (now - last_restart_time))
        log(f"Cooldown active, waiting {wait_time}s before restart")
        time.sleep(wait_time)
    
    stop_server()
    time.sleep(2)
    
    if start_server():
        time.sleep(5)
        if check_server():
            restart_attempts = 0
            last_restart_time = time.time()
            log("Server restarted successfully")
            return True
    
    restart_attempts += 1
    last_restart_time = time.time()
    log(f"Restart failed (attempt {restart_attempts}/{MAX_RESTART_ATTEMPTS})")
    return False


def handle_shutdown(signum=None, frame=None):
    global running
    log("Shutdown signal received")
    running = False


def main():
    global running, restart_attempts
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    log(f"Watchdog starting (interval: {CHECK_INTERVAL}s, max restarts: {MAX_RESTART_ATTEMPTS})")
    log(f"Monitoring: http://{HOST}:{PORT}/")
    log(f"Notifications to: {CHAT_IDS}")
    
    if not start_server():
        log("Failed to start server initially!")
        send_telegram(
            "🔴 <b>Авария при запуске</b>\n\n"
            "Не удалось запустить сервер.\n"
            f"Проверьте логи: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
        return 1
    
    time.sleep(5)
    if not check_server():
        log("Server not responding after initial start!")
        send_telegram(
            "🔴 <b>Авария при запуске</b>\n\n"
            "Сервер запущен, но не отвечает на запросы.\n"
            f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
    else:
        log("Server is healthy")
        send_telegram(
            "✅ <b>Сайт запущен</b>\n\n"
            "Мониторинг активен.\n"
            f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
    
    while running:
        time.sleep(CHECK_INTERVAL)
        
        if not running:
            break
        
        if check_server():
            restart_attempts = 0
            continue
        
        log("Server not responding!")
        
        if restart_attempts >= MAX_RESTART_ATTEMPTS:
            log("Max restart attempts reached, sending alert...")
            send_telegram(
                "🚨 <b>АВАРИЯ НА САЙТЕ</b>\n\n"
                "Сервер не поднимается после нескольких попыток рестарта.\n"
                "Требуется ручное вмешательство!\n\n"
                f"Попыток: {restart_attempts}\n"
                f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            )
            restart_attempts = 0
            time.sleep(60)
            continue
        
        log(f"Attempting restart ({restart_attempts + 1}/{MAX_RESTART_ATTEMPTS})...")
        
        if restart_server():
            send_telegram(
                "⚠️ <b>Сайт перезапущен</b>\n\n"
                "Обнаружена проблема, сервер автоматически перезапущен.\n"
                f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            )
        else:
            if restart_attempts >= MAX_RESTART_ATTEMPTS:
                send_telegram(
                    "🚨 <b>АВАРИЯ НА САЙТЕ</b>\n\n"
                    "Сервер не поднимается после рестарта!\n"
                    "Требуется ручное вмешательство!\n\n"
                    f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                )
    
    log("Watchdog shutting down...")
    stop_server()
    log("Goodbye")
    return 0


if __name__ == "__main__":
    sys.exit(main())
