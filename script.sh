#!/bin/bash
set -e

# Function to print status
function check_result() {
    if [ $? -ne 0 ]; then
        echo "[ERROR] $1 failed. Exiting."
        exit 1
    fi
    echo "[SUCCESS] $1 succeeded."
}

# Update and install system packages
echo "[INFO] Updating repositories..."
sudo apt update -y
check_result "Updating repositories"

echo "[INFO] Installing dependencies..."
sudo apt install -y git python3-venv python3-pip
check_result "Installing dependencies"

# Create virtual environment and install Python dependencies
echo "[INFO] Creating virtual environment..."
python3 -m venv _venv_
check_result "Virtual environment created"

echo "[INFO] Activating venv and installing Python requirements..."
source _venv_/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
check_result "Python dependencies installed"

# Copy systemd unit file
echo "[INFO] Installing systemd service..."
sudo cp app.service /etc/systemd/system/app.service
sudo systemctl daemon-reload
sudo systemctl enable app.service
sudo systemctl restart app.service
check_result "Systemd service installed and started"

echo "[INFO] Setup complete. Flask app should now be running on port 8080."