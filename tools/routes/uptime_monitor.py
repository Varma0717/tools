import requests
import time
from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError

uptime_monitor_bp = Blueprint('uptime_monitor', __name__, url_prefix='/tools/uptime-monitor')

@uptime_monitor_bp.route('/')
def uptime_monitor():
    return render_template('tools/uptime_monitor.html')

@uptime_monitor_bp.route('/ajax', methods=['POST'])
def uptime_monitor_ajax():
    try:
        csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({"error": "Please provide a URL to check."}), 400

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    try:
        start = time.time()
        resp = requests.get(url, timeout=10)
        duration_ms = int((time.time() - start) * 1000)
        status_code = resp.status_code
        is_up = resp.ok
    except requests.RequestException as e:
        return jsonify({
            "error": "Request failed or site is down.",
            "details": str(e)
        }), 200

    return jsonify({
        "url": url,
        "status_code": status_code,
        "response_time_ms": duration_ms,
        "is_up": is_up,
    })
