from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.link_status_monitor_utils import check_link_status

link_status_monitor_bp = Blueprint('link_status_monitor', __name__, url_prefix='/tools/link-status-monitor')

@link_status_monitor_bp.route('/', methods=['GET'])
def link_status_monitor():
    return render_template('tools/link_status_monitor.html', csrf_token=generate_csrf())

@link_status_monitor_bp.route('/ajax', methods=['POST'])
def link_status_monitor_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        raw_urls = request.form.get("urls", "").strip()
        url_list = [url.strip() for url in raw_urls.splitlines() if url.strip()]
        if not url_list:
            return jsonify({'error': 'Please enter at least one URL.'}), 400

        results = check_link_status(url_list)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
