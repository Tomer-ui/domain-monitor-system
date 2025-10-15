# Domain Monitor System

flask based web-based application to monitor domain status, SSL certificate validity, via a web interface & a RESTful API 

## Features

*   User registration and login
*   Dashboard to view monitored domains
*   Real-time domain status checking (Live/Unavailable)
*   SSL certificate expiration and issuer information
*   Add and remove domains individually
*   Bulk upload domains from a .txt file

## Project Structure
```
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
├── API_DOCUMENTATION.md
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

### Prerequisites

*   Python 3.8+

### 1. Create a Virtual Environment
It is recommended to use a virtual environment to manage the project's dependencies.

### 2. Install Requirements
With the virtual environment activated, install the necessary packages from the requirements.txt file,  pip install -r requirements.txt

### 3. Run the Application
Execute the app.py file to start the Flask development server.
The application will be accessible at http://127.0.0.1:8080 in your web browser.

**How to Use**
Register: Create a new account through the registration page.
Login: Log in with your credentials.
Dashboard: After logging in, you will be redirected to the dashboard, where you can:
Add a single domain using the input field.
Bulk upload domains from a .txt file (one domain per line).
View the status of your monitored domains.
Remove domains from your list.


## API Documentation

The backend provides a complete RESTful API for all user and domain management operations. For detailed information on every endpoint, including request formats, response examples, and status codes, please see the full guide:

**[View the Full API Documentation](/API_DOCUMENTATION.md)**