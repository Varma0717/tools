from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError

request_rate_monitor_bp = Blueprint('request_rate_monitor', __name__, url_prefix='/tools')

# Simple in-memory store for example (replace with Redis/db for production)
ip_request_counts = {}

@request_rate_monitor_bp.route('/request-rate-monitor')
def request_rate_monitor():
    return render_template('tools/request_rate_monitor.html')

@request_rate_monitor_bp.route('/request-rate-monitor/ajax', methods=['POST'])
def request_rate_monitor_ajax():
    try:
        csrf_token = request.headers.get('X-CSRFToken') or request.json.get('csrf_token')
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Increment count for IP
    ip_request_counts[ip] = ip_request_counts.get(ip, 0) + 1

    # Return current count and sample stats
    data = {
        "ip": ip,
        "request_count": ip_request_counts[ip],
        # In real app, add timestamp-based rate or limit info
        "message": "Request count incremented for your IP."
    }
    return jsonify(data)
