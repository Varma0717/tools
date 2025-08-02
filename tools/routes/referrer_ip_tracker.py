from flask import Blueprint, request, jsonify, render_template

from flask_wtf.csrf import validate_csrf, CSRFError

referrer_ip_tracker_bp = Blueprint('referrer_ip_tracker', __name__, url_prefix='/tools')

@referrer_ip_tracker_bp.route('/referrer-ip-tracker')

def referrer_ip_tracker():
    # Render tool page (with CSRF token passed automatically)
    return render_template('tools/referrer_ip_tracker.html')

@referrer_ip_tracker_bp.route('/referrer-ip-tracker/ajax', methods=['POST'])
def referrer_ip_tracker_ajax():
    try:
        # Validate CSRF token from headers or JSON payload
        csrf_token = request.headers.get('X-CSRFToken') or request.json.get('csrf_token')
        validate_csrf(csrf_token)   
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    # Get client IP and referrer info
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    referrer = request.headers.get('Referer', 'No referrer header')
    user_agent = request.headers.get('User-Agent', 'Unknown')

    # Build response data (customize as needed)
    data = {
        "ip": ip,
        "referrer": referrer,
        "user_agent": user_agent,
    }
    return jsonify(data)
