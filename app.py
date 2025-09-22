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


@app.route('/health', methods=['GET'])
def healthcheck():
    return jsonify({'status': 'healthy'}), 200


@app.route('/')
def main():
    if 'username' in session:
        return redirect(url_for('deshboard'))
    logger.info("serving lgoin .html for anonymous user")
    return render_template('login.html')



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
            #NEW - "flash" a success message before redirect.
            flash('login successful!', 'success')
            return redirect(url_for('deshboard'))
        else:
            flash(message, 'error')
            return render_template('login.html', error=message)
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('you have been logged out.', 'info') #NEW - flash an info message.
    return redirect(url_for('main'))


@app.route('/deshboard')
def deshboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    logger.info(f"generating deshboard for user: {username}.")
    #1.get the current list of domains from user file.
    domains_to_check = get_user_domains(username)
    domain_names = [d['domain'] for d in domains_to_check]

    if not domain_names:
        return render_template('deshboard.html', username=username, results=[])
    
    #2.run the concurrent check to get freash data
    fresh_check_results = check_domains_concurrently(domain_names)

    #3.format the data into desired structure
    final_report =[]
    for result in fresh_check_results:
        status_code = result.get('status_code')
        if status_code == 200:
            status_text = f"live. status code {status_code}"
        else:
            status_text = f"unavailable. status code {status_code}"

        #here we "map" the check output to the desired json structure
        formatted_result = {
            "domain": result.get('domain'),
            "status": status_text,
            "ssl_expiration": result.get('certificate_expiry', 'N/A'),
            "ssl_issuer": result.get('issuer', 'N/A')
        }
        final_report.append(formatted_result)
    #4. save fresh data. overwrite old file.
    save_user_domains(username, final_report)
    #5. render the page using the data.
    return render_template('deshboard.html', username=username, results = final_report)



@app.route('/add_domain', methods= ['POST'])
def add_domain():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    domain_to_add = request.form['domain'].strip()

    if domain_to_add:
        current_domains = get_user_domains(username)
        if domain_to_add not in [d['domain']for d in current_domains]:
            #add the new domain
            current_domains.append({
                "domain": domain_to_add,
                "status": "pending check",
                "ssl_expiration": "N/A",
                "ssl_issuer": "N/A"
            })
            save_user_domains(username, current_domains)

    return redirect(url_for('deshboard'))



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
        return redirect(url_for('deshboard'))
    
    if not file.filename.endswith('.txt'):
        return "error: please upload a valid .txt file.", 400
    
    #4.process file
    username = session['username']
    current_domains = get_user_domains(username)
    #making a "set" of domains,
    existing_domain_names = {d['domain'] for d in current_domains}

    #read file line by line
    for line in file.readlines():
        #the lines are read as bytes, we need to decode them to strings
        #.strip() removes any whitespace or newline chars.
        domain = line.decode('utf-8').strip() #goooood luck stack overflow this !@#!$@ ty chat.
        #add the domain if the line isnt empty & if the domain is "UNIQ"
        if domain and domain not in existing_domain_names:
            current_domains.append({
                "domain": domain,
                "status": "pending check",
                "ssl_expiration": "N/A",
                "ssl_issuer": "N/A"
            })

            existing_domain_names.add(domain)
    #5.save the updated list of domains
    save_user_domains(username, current_domains)
    #6.redirect back to the deshboard to see new added domains. ^_^
    return redirect(url_for('deshboard'))


@app.route('/remove_domain', methods=['POST'])
def remove_domain():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    domain_to_remove = request.form['domain']

    if not domain_to_remove:
        flash('invalid request.' , 'error')
        return redirect(url_for('deshboard'))
    
    #call data_manger.py to handle deletion
    success = remove_user_domain(username, domain_to_remove)
    #based on result, 'flash' appropriate message.
    if success:
        flash(f"domain '{domain_to_remove}' was removed successfully." , 'success')
    else:
        flash(f"domain '{domain_to_remove}' was not found in your list.", 'warning')
    #time to go back home.
    return redirect(url_for('deshboard'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8080")