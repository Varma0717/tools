import os
import io
import csv
from urllib.parse import urlparse

from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError

referrer_spam_filter_bp = Blueprint('referrer_spam_filter', __name__, url_prefix='/tools/referrer-spam-filter')

def load_spam_domains():
    spam_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'referrer_spam_domains.txt')
    with open(spam_file, 'r', encoding='utf-8') as f:
        domains = [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
    return set(domains)

SPAM_DOMAINS = load_spam_domains()

@referrer_spam_filter_bp.route('/')
def referrer_spam_filter():
    return render_template('tools/referrer_spam_filter.html')

@referrer_spam_filter_bp.route('/ajax', methods=['POST'])
def referrer_spam_filter_ajax():
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

        clean_referrers = []
        spam_referrers = []

        for row in reader:
            if not row:
                continue
            ref_url = row[0].strip()
            if not ref_url or ref_url == '-':
                continue

            domain = urlparse(ref_url).netloc.lower()
            if any(spam_domain in domain for spam_domain in SPAM_DOMAINS):
                spam_referrers.append(ref_url)
            else:
                clean_referrers.append(ref_url)

        return jsonify({
            "clean_count": len(clean_referrers),
            "spam_count": len(spam_referrers),
            "clean_referrers": clean_referrers[:20],  # limit to 20 entries
            "spam_referrers": spam_referrers[:20],
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
