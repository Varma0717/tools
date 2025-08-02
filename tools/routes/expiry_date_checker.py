# tools/routes/expiry_date_checker.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
import whois

expiry_date_checker_bp = Blueprint('expiry_date_checker', __name__, url_prefix='/tools')

# Fetch domain expiry date via python-whois
# pip install python-whois
def get_expiry_date(domain_url):
    try:
        domain = domain_url.split("//")[-1].split("/")[0]
        w = whois.whois(domain)
        expiry = w.expiration_date
        if isinstance(expiry, list) and expiry:
            expiry = expiry[0]
        expiry_str = expiry.strftime("%Y-%m-%d") if hasattr(expiry, 'strftime') else str(expiry)
        return {"domain": domain, "expiry": expiry_str}
    except Exception as e:
        return {"error": f"WHOIS lookup failed: {e}"}

@expiry_date_checker_bp.route('/expiry-date-checker', methods=['GET'])
def expiry_date_checker():
    csrf_token = generate_csrf()
    return render_template('tools/expiry_date_checker.html', csrf_token=csrf_token)

@expiry_date_checker_bp.route('/expiry-date-checker/ajax', methods=['POST'])
def expiry_date_checker_ajax():
    try:
        data = request.get_json() or {}
        url = data.get('url', '').strip()
        csrf_token = request.headers.get('X-CSRFToken', '')
        # Validate CSRF
        try:
            validate_csrf(csrf_token)
        except Exception:
            return jsonify({"error": "CSRF token missing or invalid."}), 400
        # Validate input
        if not url:
            return jsonify({"error": "Enter a valid domain URL."}), 400
        # Fetch expiry
        result = get_expiry_date(url)
        return jsonify(result)
    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({"error": f"Unexpected error: {e}"}), 200
