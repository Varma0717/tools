from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.backlink_url_monitor_utils import monitor_backlinks

backlink_url_monitor_bp = Blueprint('backlink_url_monitor', __name__, url_prefix='/tools/backlink-url-monitor')

@backlink_url_monitor_bp.route('/', methods=['GET'])
def backlink_url_monitor():
    return render_template('tools/backlink_url_monitor.html', csrf_token=generate_csrf())

@backlink_url_monitor_bp.route('/ajax', methods=['POST'])
def backlink_url_monitor_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        target = request.form.get("target", "").strip()
        sources_raw = request.form.get("urls", "").strip()

        if not target or not sources_raw:
            return jsonify({'error': 'Please enter both target URL and backlink URLs.'}), 400

        sources = [url.strip() for url in sources_raw.splitlines() if url.strip()]
        results = monitor_backlinks(target, sources)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
