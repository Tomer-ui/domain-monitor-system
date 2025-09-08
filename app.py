from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from domain_checker import check_domain_status, check_domains_concurrently
from logs import logger
from user_management import register_user, login_user
from data_manager import get_user_domains, save_user_domains
import os


load_dotenv()
app = Flask(__name__, template_folder= 'templates', static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")


@app.route('/health', methods=['GET'])
def healthcheck():
    return jsonify({'status': 'healthy'}), 200


@app.route('/')
def main():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    logger.info("serving main.html for anonymous user")
    return render_template('main.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username =request.form['username']
        password = request.form['password']
        success, message = register_user(username, password)
        if success:
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error=message)
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success, message = login_user(username, password)
        if success:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error=message)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_domains_list = get_user_domains(username)
    domain_names = [d['domain'] for d in user_domains_list]
    #here using concurrent checker for performance
    domain_statuses = check_domains_concurrently(domain_names)
    return render_template('dashboard.html', domains=domain_statuses)



@app.route('/add_domain', methods= ['POST'])
def add_domain():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    domain = request.form['domain']

    #importing functions from data_manager.py 
    domains = get_user_domains(username)
    domains.append({'domain': domain, 'status': 'pending', 'ssl_expiration': 'N/A', 'ssl_issuer': 'N/A'})
    save_user_domains(username, domains)

    return redirect(url_for('dashboard'))



@app.route('/bulk_upload', methods=['POST'])
def bulk_upload():
    #1.ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    #2.get the file from the request
    file = request.files.get('file')

    #3.validation if a file was submited,
    #  & has the right extension
    if not file or file.filename == '':
        logger.error(f"problem with file, please check again")
        return redirect(url_for('dashboard'))
    
    if not file.filename.endswith('.txt'):
        return "error: please upload a valid .txt file.", 400
    
    #4.process file
    username = session['username']
    domains = get_user_domains(username)
    #read file line by line
    for line in file.readlines():
        #the lines are read as bytes, we need to decode them to strings
        #.strip() removes any whitespace or newline chars.
        domain = line.decode('utf-8').strip() #goooood luck stack overflow this !@#!$@ ty chat.
        #add the domain if the line isnt empty
        # & if the domain is "UNIQ"
        if domain not in [d['domain']for d in domains]:
            domains.append({
                'domain': domain,
                'status': 'pending',
                'ssl_expiration': 'N/A',
                'ssl_issuer': 'N/A'
            })
    #5.save the updated list of domains
    save_user_domains(username, domains)
    #6.redirect back to the dashboard to see new added domains. ^_^
    return redirect(url_for('dashboard'))



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8080")
