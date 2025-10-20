#!/bin/bash
set -e  # exit on any error

echo "[INFO] Starting deployment of Domain Monitor System..."

# -----------------------------
# Variables
# -----------------------------
APP_DIR="$HOME/domain-monitor-system"
REPO_URL="https://github.com/Tomer-ui/domain-monitor-system.git"

# -----------------------------
# Install system dependencies
# -----------------------------
echo "[INFO] Updating repositories..."
sudo apt update -y
echo "[SUCCESS] Repositories updated."

echo "[INFO] Installing required packages..."
sudo apt install -y git python3-venv python3-pip
echo "[SUCCESS] Dependencies installed."

# -----------------------------
# Clone or update the repo
# -----------------------------
if [ -d "$APP_DIR" ]; then
    echo "[INFO] Repo exists. Pulling latest changes..."
    cd "$APP_DIR"
    git reset --hard
    git pull
else
    echo "[INFO] Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi
echo "[SUCCESS] Repo ready at $APP_DIR"

# -----------------------------
# Create virtual environment
# -----------------------------
if [ ! -d "_venv_" ]; then
    echo "[INFO] Creating Python virtual environment..."
    python3 -m venv _venv_
else
    echo "[INFO] Virtual environment already exists."
fi

# Activate venv and install Python dependencies
echo "[INFO] Installing Python requirements..."
source _venv_/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "[SUCCESS] Python dependencies installed."

# -----------------------------
# Configure systemd service
# -----------------------------
SERVICE_FILE="/etc/systemd/system/app.service"

echo "[INFO] Installing systemd service..."
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Domain Liveness Check Flask App
After=network.target
Wants=network-online.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/_venv_/bin/python3 $APP_DIR/app.py
Environment=\"PATH=$APP_DIR/_venv_/bin\"
Environment=\"FLASK_ENV=production\"
Environment=\"PYTHONUNBUFFERED=1\"
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable app.service
sudo systemctl restart app.service
echo "[SUCCESS] Systemd service installed and started."

echo "[INFO] Deployment complete! Flask app is running on port 8080."
