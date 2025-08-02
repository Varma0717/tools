from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.link_profile_analyzer_utils import analyze_link_profile

link_profile_analyzer_bp = Blueprint('link_profile_analyzer', __name__, url_prefix='/tools/link-profile-analyzer')

@link_profile_analyzer_bp.route('/', methods=['GET'])
def link_profile_analyzer():
    return render_template('tools/link_profile_analyzer.html', csrf_token=generate_csrf())

@link_profile_analyzer_bp.route('/ajax', methods=['POST'])
def link_profile_analyzer_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        url = request.form.get("url", "").strip()
        if not url:
            return jsonify({'error': 'Please enter a valid page URL.'}), 400

        results = analyze_link_profile(url)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
