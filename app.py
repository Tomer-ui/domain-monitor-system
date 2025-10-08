from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, flash
from domain_checker import check_domains_concurrently
from logs import logger
from user_management import register_user, login_user
from data_manager import get_user_domains, save_user_domains, remove_user_domain
import os


load_dotenv()
app = Flask(__name__, template_folder= 'templates', static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")


# =================================================================
# MODIFICATION: HTML Page Serving Routes
# These routes now ONLY serve the HTML templates. All data logic is moved
# to the API endpoints below.
# ==================================================================

@app.route('/')
def main_page():
    # If the user has a session, show them the dashboard, otherwise the login page.
    if 'username' in session:
        return redirect(url_for('dashboard_page'))
    return redirect(url_for('login_page'))

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    # This route is now protected; it will only serve the dashboard if the user is logged in.
    if 'username' not in session:
        return redirect(url_for('login_page'))
    # The template is rendered without data; the frontend JS will fetch it.
    return render_template('dashboard.html', username=session['username'])


# =================================================================
# MODIFICATION: New JSON API Endpoints
# These endpoints fulfill the LLD requirement for a JSON-based API.
# =================================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"success": False, "message": "Username and password are required."}), 400
    
    username = data['username']
    password = data['password']
    
    success, message = register_user(username, password)
    
    if success:
        return jsonify({"success": True, "message": "Registration successful"}), 201
    else:
        # Common error for existing user is a conflict
        status_code = 409 if "exists" in message else 500
        return jsonify({"success": False, "message": message}), status_code

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    username = data['username']
    password = data['password']

    success, message = login_user(username, password)

    if success:
        session['username'] = username
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        # Invalid credentials is an unauthorized error
        return jsonify({"success": False, "message": message}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    return jsonify({"success": True, "message": "You have been logged out."}), 200

@app.route('/api/session', methods=['GET'])
def api_session():
    # A new endpoint for the frontend to check if a user is logged in.
    if 'username' in session:
        return jsonify({"loggedIn": True, "username": session['username']}), 200
    else:
        return jsonify({"loggedIn": False}), 401

@app.route('/api/domains', methods=['GET'])
def api_get_domains():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    logger.info(f"API: fetching and checking domains for user: {username}.")
    
    domains_to_check = get_user_domains(username)
    domain_names = [d['domain'] for d in domains_to_check]

    if not domain_names:
        return jsonify([]) # Return empty list if no domains

    fresh_check_results = check_domains_concurrently(domain_names)

    final_report =[]
    for result in fresh_check_results:
        status_code = result.get('status_code')
        status_text = f"Live. Status code {status_code}" if status_code == 200 else f"Unavailable. Status code {status_code}"
        formatted_result = {
            "domain": result.get('domain'),
            "status": status_text,
            "ssl_expiration": result.get('certificate_expiry', 'N/A'),
            "ssl_issuer": result.get('issuer', 'N/A')
        }
        final_report.append(formatted_result)

    save_user_domains(username, final_report)
    return jsonify(final_report)

@app.route('/api/add_domain', methods=['POST'])
def api_add_domain():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    domain_to_add = data.get('domain', '').strip()

    if not domain_to_add:
        return jsonify({"success": False, "message": "Domain cannot be empty."}), 400

    username = session['username']
    current_domains = get_user_domains(username)

    if domain_to_add in [d['domain'] for d in current_domains]:
        return jsonify({"success": False, "message": f"Domain '{domain_to_add}' is already in your list."}), 409

    current_domains.append({
        "domain": domain_to_add, "status": "Pending check", "ssl_expiration": "N/A", "ssl_issuer": "N/A"
    })
    save_user_domains(username, current_domains)
    return jsonify({"success": True, "message": f"Domain '{domain_to_add}' was added successfully."}), 201

@app.route('/api/remove_domain', methods=['POST'])
def api_remove_domain():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    domain_to_remove = request.get_json().get('domain')

    if not domain_to_remove:
        return jsonify({"success": False, "message": "Invalid request."}), 400
    
    success = remove_user_domain(username, domain_to_remove)
    if success:
        return jsonify({"success": True, "message": f"Domain '{domain_to_remove}' was removed."}), 200
    else:
        return jsonify({"success": False, "message": f"Domain '{domain_to_remove}' not found."}), 404

@app.route('/api/bulk_upload', methods=['POST'])
def api_bulk_upload():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    file = request.files.get('file')

    if not file or file.filename == '' or not file.filename.endswith('.txt'):
        return jsonify({"success": False, "message": "Please upload a valid .txt file."}), 400
    
    username = session['username']
    current_domains = get_user_domains(username)
    existing_domain_names = {d['domain'] for d in current_domains}
    added_count = 0

    for line in file.readlines():
        domain = line.decode('utf-8').strip()
        if domain and domain not in existing_domain_names:
            current_domains.append({
                "domain": domain, "status": "pending check", "ssl_expiration": "N/A", "ssl_issuer": "N/A"
            })
            existing_domain_names.add(domain)
            added_count += 1
            
    save_user_domains(username, current_domains)
    return jsonify({"success": True, "message": f"Bulk upload complete. Added {added_count} new domains."}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8080")