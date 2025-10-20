#!/bin/bash

function check_result() {
        if [ $? -ne 0 ]; then
                echo "[ERROR] $1 failed. Exiting."
                exit 1
        fi
        echo "[SUCCESS] $1 succeeded."
}
sudo su -
apt update -y
check_result "Updating repsitories"
git clone https://github.com/Tomer-ui/domain-monitor-system.git
check_result "Downloading git repository"
cd domain-monitor-system/
python3 -m venv _venv_
source _venv_/bin/activate
check_result "Creating virtual environment"
pip3 install -r requirements.txt -y
check_result "Installing requirements"
cp app.service /etc/system/systemd/app.service
systemctl daemon-reload
systemctl start app.service
systemctl enable app.service
check_result "Starting service and enabling on boot startup"