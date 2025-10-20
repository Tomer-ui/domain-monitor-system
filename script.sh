#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check result and exit if failure
function check_result() {
    if [ $? -ne 0 ]; then
        echo "[ERROR] $1 failed. Exiting."
        exit 1
    fi
    echo "[SUCCESS] $1 succeeded."
}

echo "[INFO] Updating repositories..."
sudo apt update -y
check_result "Updating repositories"

echo "[INFO] Installing dependencies..."
sudo apt install -y git python3-venv python3-pip
check_result "Installing dependencies"

echo "[INFO] Removing old repo (if exists)..."
rm -rf domain-monitor-system

echo "[INFO] Cloning repository..."
git clone https://github.com/Tomer-ui/domain-monitor-system.git
check_result "Cloning repository"

cd domain-monitor-system

echo "[INFO] Creating virtual environment..."
python3 -m venv _venv_
check_result "Creating virtual environment"

echo "[INFO] Activating virtual environment and installing requirements..."
source _venv_/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
check_result "Installing Python dependencies"

echo "[INFO] Copying systemd service file..."
sudo cp app.service /etc/systemd/system/app.service
check_result "Copying systemd service file"

echo "[INFO] Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "[INFO] Starting Flask service..."
sudo systemctl enable app.service
sudo systemctl restart app.service
check_result "Starting and enabling service"

echo "[INFO] Setup complete. Flask app should now be running on port 8080."