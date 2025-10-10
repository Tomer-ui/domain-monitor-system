# Domain Monitor System

A web-based application to monitor domain status, SSL certificate validity, and other relevant information.

## Features

*   User registration and login
*   Dashboard to view monitored domains
*   Real-time domain status checking (Live/Unavailable)
*   SSL certificate expiration and issuer information
*   Add and remove domains individually
*   Bulk upload domains from a .txt file

## Project Structure
'''
.
├── .venv/
├── data/
├── static/
│ ├── dashboard.css
│ ├── dashboard.js
│ ├── login.css
│ ├── login.js
│ ├── register.css
│ └── register.js
├── templates/
│ ├── dashboard.html
│ ├── login.html
│ └── register.html
├── .gitignore
├── app.py
├── data_manager.py
├── domain_checker.log
├── domain_checker.py
├── logs.py
├── requirements.txt
├── users.json
└── user_management.py
...

## Setup and Installation

### 1. Create a Virtual Environment
It is recommended to use a virtual environment to manage the project's dependencies.
### 2. Install Requirements
With the virtual environment activated, install the necessary packages from the requirements.txt file.
### 3. Run the Application
Execute the app.py file to start the Flask development server.

The application will be accessible at http://127.0.0.1:8080 in your web browser.
