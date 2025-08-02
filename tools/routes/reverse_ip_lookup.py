# tools/routes/reverse_ip_lookup.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, IPAddress
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
import requests

csrf = CSRFProtect()
reverse_ip_lookup_bp = Blueprint('reverse_ip_lookup', __name__, url_prefix='/tools')

class ReverseIPForm(FlaskForm):
    ip = StringField('Server IP Address', validators=[DataRequired(), IPAddress()])
    submit = SubmitField('Find Hosted Domains')

def perform_reverse_ip(ip):
    # Placeholder for future custom implementation
    own_results = try_own_reverse_ip(ip)
    if own_results:
        return own_results
    # Fallback to external API
    return fallback_hackertarget(ip)

def try_own_reverse_ip(ip):
    # You can build your own logic here in the future
    # For now, return empty to simulate fallback
    return []

def fallback_hackertarget(ip):
    try:
        url = f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            lines = resp.text.strip().splitlines()
            if "error" in lines[0].lower():
                return {"error": lines[0]}
            return lines
        return {"error": f"API error: {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

@reverse_ip_lookup_bp.route('/reverse-ip-lookup', methods=['GET'])
def reverse_ip_lookup():
    form = ReverseIPForm()
    csrf_token = generate_csrf()
    return render_template('tools/reverse_ip_lookup.html', form=form, csrf_token=csrf_token)

@reverse_ip_lookup_bp.route('/reverse-ip-lookup/ajax', methods=['POST'])
def reverse_ip_lookup_ajax():
    try:
        validate_csrf(request.headers.get("X-CSRFToken"))
    except Exception:
        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

    data = request.get_json()
    ip = data.get('ip', '').strip()
    if not ip:
        return jsonify({"success": False, "error": "Please provide a valid IP address."})

    results = perform_reverse_ip(ip)
    if isinstance(results, dict) and "error" in results:
        return jsonify({"success": False, "error": results["error"]})

    return jsonify({"success": True, "domains": results, "source": "Super SEO Toolkit Scanner"})
