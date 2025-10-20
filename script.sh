#!/bin/bash

function check_result() {
    if [ $? -ne 0 ]; then
        echo "[ERROR] $1 failed. Exiting."
        exit 1
    fi
    echo "[SUCCESS] $1 succeeded."
}

apt update -y
check_result "Updating repositories"

apt install -y git python3-venv python3-pip
check_result "Installing dependencies"

rm -rf domain-monitor-system
git clone https://github.com/Tomer-ui/domain-monitor-system.git
check_result "Downloading git repository"

cd domain-monitor-system/

python3 -m venv venv
source venv/bin/activate
check_result "Creating virtual environment"

pip install -r requirements.txt
check_result "Installing requirements"

sudo cp app.service /etc/systemd/system/app.service
sudo systemctl daemon-reload
sudo systemctl start app.service
sudo systemctl enable app.service
check_result "Starting service and enabling on boot startup"