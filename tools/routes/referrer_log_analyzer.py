import csv
import io
from collections import Counter, defaultdict
from urllib.parse import urlparse

from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError

referrer_log_analyzer_bp = Blueprint('referrer_log_analyzer', __name__, url_prefix='/tools/referrer-log-analyzer')

@referrer_log_analyzer_bp.route('/')
def referrer_log_analyzer():
    return render_template('tools/referrer_log_analyzer.html')

@referrer_log_analyzer_bp.route('/ajax', methods=['POST'])
def referrer_log_analyzer_ajax():
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
        reader = csv.reader(stream)

        referrers = []
        for row in reader:
            # Assume referrer URL is in first column, adapt if needed
            if not row:
                continue
            ref_url = row[0].strip()
            if not ref_url or ref_url == '-':
                continue
            referrers.append(ref_url)

        total_visits = len(referrers)
        unique_referrers = len(set(referrers))

        # Count domains
        domain_counts = Counter()
        for url in referrers:
            parsed = urlparse(url)
            domain = parsed.netloc.lower() if parsed.netloc else 'unknown'
            domain_counts[domain] += 1

        top_domains = domain_counts.most_common(10)

        # Optionally: flag suspicious domains (basic example)
        suspicious = [d for d, c in top_domains if 'spam' in d or 'bot' in d]

        return jsonify({
            "total_visits": total_visits,
            "unique_referrers": unique_referrers,
            "top_domains": top_domains,
            "suspicious_domains": suspicious,
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
