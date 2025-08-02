import io
import csv
from collections import Counter
from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError

click_fraud_detector_bp = Blueprint('click_fraud_detector', __name__, url_prefix='/tools/click-fraud-detector')

@click_fraud_detector_bp.route('/')
def click_fraud_detector():
    return render_template('tools/click_fraud_detector.html')

@click_fraud_detector_bp.route('/ajax', methods=['POST'])
def click_fraud_detector_ajax():
    try:
        csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    if 'logfile' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    logfile = request.files['logfile']
    if logfile.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        stream = io.StringIO(logfile.stream.read().decode("utf-8", errors="ignore"))
        reader = csv.DictReader(stream)

        ip_counts = Counter()
        suspicious_ips = set()

        for row in reader:
            ip = row.get('ip') or row.get('IP') or row.get('client_ip') or row.get('ClientIP') or ''
            if not ip:
                continue
            ip_counts[ip] += 1

        # Simple heuristic: flag IPs with > threshold clicks (e.g., > 10)
        threshold = 10
        for ip, count in ip_counts.items():
            if count > threshold:
                suspicious_ips.add(ip)

        return jsonify({
            "total_clicks": sum(ip_counts.values()),
            "unique_ips": len(ip_counts),
            "suspicious_ips": list(suspicious_ips),
            "ip_clicks": ip_counts.most_common(10)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
