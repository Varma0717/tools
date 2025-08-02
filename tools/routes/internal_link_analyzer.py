from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.internal_link_analyzer_utils import extract_internal_links

internal_link_analyzer_bp = Blueprint('internal_link_analyzer', __name__, url_prefix='/tools/internal-link-analyzer')

@internal_link_analyzer_bp.route('/', methods=['GET'])
def internal_link_analyzer():
    return render_template('tools/internal_link_analyzer.html', csrf_token=generate_csrf())

@internal_link_analyzer_bp.route('/ajax', methods=['POST'])
def internal_link_analyzer_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        url = request.form.get("url", "").strip()
        if not url:
            return jsonify({'error': 'Please enter a valid website URL.'}), 400

        links = extract_internal_links(url)
        return jsonify({'results': links})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
