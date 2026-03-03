#!/bin/bash
# ============================================================
#  tepliy-dom — Первоначальная настройка сервера (Ubuntu 22/24)
#  Запуск: curl -sL <raw-url> | bash
#  Или: bash setup-server.sh
# ============================================================
set -euo pipefail

REPO_URL="https://github.com/LLIaJIoM/-----------------main1-main.git"
INSTALL_DIR="/opt/tepliy-dom"
SERVICE_NAME="tepliy-dom"
SERVER_PORT=8000

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✔]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✘]${NC} $1"; exit 1; }

# ── Проверки ──────────────────────────────────────────────
[[ $EUID -ne 0 ]] && err "Запустите от root: sudo bash $0"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  tepliy-dom — Setup Server"
echo "═══════════════════════════════════════════════════"
echo ""

# ── 1. Обновление системы ─────────────────────────────────
log "Обновление системы..."
apt-get update -qq
apt-get upgrade -y -qq

# ── 2. Установка зависимостей ─────────────────────────────
log "Установка Python 3, pip, git..."
apt-get install -y -qq python3 python3-pip python3-venv git curl

# ── 3. Клонирование репозитория ───────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
    warn "Репозиторий уже клонирован в $INSTALL_DIR"
    cd "$INSTALL_DIR"
    git pull origin main || true
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    log "Репозиторий склонирован в $INSTALL_DIR"
fi

# ── 4. Установка Python-зависимостей ─────────────────────
log "Установка Python-зависимостей..."
pip3 install --break-system-packages -r requirements.txt --quiet 2>/dev/null || true

# ── 5. Файл окружения (.env) ─────────────────────────────
if [ ! -f "$INSTALL_DIR/.env" ]; then
    log "Создание .env..."
    cat > "$INSTALL_DIR/.env" <<'ENVEOF'
# Telegram уведомления
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_CHAT_IDS=

# Сервер
HOST=0.0.0.0
PORT=8000

# Watchdog
WATCHDOG_INTERVAL=60
WATCHDOG_MAX_RESTARTS=3
WATCHDOG_COOLDOWN=300
ENVEOF
    warn "Заполните $INSTALL_DIR/.env вашими данными!"
else
    log ".env уже существует"
fi

# ── 6. SSH-ключ для GitHub Actions ────────────────────────
KEY_PATH="/root/.ssh/actions_key"
if [ ! -f "$KEY_PATH" ]; then
    log "Генерация SSH-ключа для GitHub Actions..."
    ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "github-actions-deploy"
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "  Добавьте этот ключ в GitHub Secrets:"
    echo "  Settings → Secrets → SERVER_SSH_KEY"
    echo "═══════════════════════════════════════════════════"
    echo ""
    cat "$KEY_PATH"
    echo ""
    echo "═══════════════════════════════════════════════════"

    # Добавляем публичный ключ в authorized_keys
    mkdir -p /root/.ssh
    cat "${KEY_PATH}.pub" >> /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
    log "Публичный ключ добавлен в authorized_keys"
else
    warn "SSH-ключ уже существует: $KEY_PATH"
fi

# ── 7. Systemd-сервис ────────────────────────────────────
log "Создание systemd-сервиса..."
cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<SVCEOF
[Unit]
Description=Tepliy Dom Website (watchdog + server)
After=network.target
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
EnvironmentFile=${INSTALL_DIR}/.env
ExecStart=/usr/bin/python3 ${INSTALL_DIR}/watchdog.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"
log "Сервис $SERVICE_NAME запущен и включён в автозагрузку"

# ── 8. Проверка ───────────────────────────────────────────
sleep 5
if curl -sf "http://127.0.0.1:${SERVER_PORT}/" > /dev/null 2>&1; then
    log "Сервер работает на порту $SERVER_PORT ✅"
else
    warn "Сервер ещё запускается... проверьте: systemctl status $SERVICE_NAME"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Установка завершена!"
echo ""
echo "  Путь:    $INSTALL_DIR"
echo "  Сервис:  systemctl status $SERVICE_NAME"
echo "  Логи:    journalctl -u $SERVICE_NAME -f"
echo "  Порт:    $SERVER_PORT"
echo ""
echo "  GitHub Secrets (обязательно!):"
echo "    SERVER_HOST  = IP вашего сервера"
echo "    SERVER_SSH_KEY = содержимое $KEY_PATH"
echo "    GH_PAT = ваш GitHub Personal Access Token"
echo "═══════════════════════════════════════════════════"
echo ""
