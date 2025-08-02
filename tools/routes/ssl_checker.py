# tools/routes/ssl_checker.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
import ssl, socket
from urllib.parse import urlparse
import datetime

ssl_checker_bp = Blueprint('ssl_checker', __name__, url_prefix='/tools')

def check_ssl(url):
    try:
        hostname = urlparse(url).netloc
        if not hostname:
            raise Exception("Invalid URL.")
        port = 443
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=8) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                issued_to = cert.get('subject', (('', ''),))[0][0][1] if cert.get('subject') else ""
                issued_by = cert.get('issuer', (('', ''),))[0][0][1] if cert.get('issuer') else ""
                not_before = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (not_after - datetime.datetime.utcnow()).days
                valid = ssock.version() is not None
                return {
                    "hostname": hostname,
                    "issued_to": issued_to,
                    "issued_by": issued_by,
                    "not_before": not_before.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "not_after": not_after.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "days_left": days_left,
                    "protocol": ssock.version(),
                    "valid": valid,
                }
    except Exception as e:
        return {"error": str(e)}

@ssl_checker_bp.route('/ssl-checker', methods=['GET'])
def ssl_checker():
    csrf_token = generate_csrf()
    return render_template('tools/ssl_checker.html', csrf_token=csrf_token)

@ssl_checker_bp.route('/ssl-checker/ajax', methods=['POST'])
def ssl_checker_ajax():
    data = request.get_json()
    url = data.get('url', '').strip()
    csrf_token = request.headers.get("X-CSRFToken", "")
    try:
        validate_csrf(csrf_token)
    except Exception:
        return jsonify({"error": "CSRF token missing or invalid."}), 400
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"error": "Enter a valid website URL (include https://)."}), 400
    ssl_info = check_ssl(url)
    if "error" in ssl_info:
        return jsonify({"error": ssl_info["error"]}), 200
    return jsonify(ssl_info)
