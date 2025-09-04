from datetime import datetime, timezone
from flask import Flask, jsonify, request, render_template, send_from_directory
from domain_checker import check_domain_status
from logs import logger

app = Flask(__name__, static_url_path='', static_folder='static')

@app.route('/health', methods=['GET'])
def healthcheck():
    return jsonify({'status': 'healthy'}), 200


@app.route('/')
def main():
    logger.info("serving main.html")
    return render_template('main.html')


@app.route('/time')
def time():
    now_time = datetime.now().strftime("%b %d %H:%M:%S %Y %Z")
    logger.info("serving sergei.html") 
    return send_from_directory('static', 'sergei.html')
    # return now_time


@app.route('/check_domain', methods=['GET'])
def get_domain_health():
    domain = request.args.get('domain')
    if not domain:
        logger.warning("request received without a domain parameter.")
        return jsonify({'error': 'domain parameter is required'}), 400

    logger.info(f"received request to check domain: {domain}")
    report = check_domain_status(domain)

    # add the health status check
    if report['status_code'] == 200 and report['certificate_status'] == 'valid':
        report['healthy'] = True
    else:
        report['healthy'] = False

    return jsonify(report)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8080")
