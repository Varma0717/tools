from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.seo_audit_tool_utils import audit_seo

seo_audit_tool_bp = Blueprint('seo_audit_tool', __name__, url_prefix='/tools/seo-audit')

@seo_audit_tool_bp.route('/', methods=['GET'])
def seo_audit():
    return render_template('tools/seo_audit_tool.html', csrf_token=generate_csrf())

@seo_audit_tool_bp.route('/ajax', methods=['POST'])
def seo_audit_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        url = request.form.get("url", "").strip()
        if not url:
            return jsonify({'error': 'Please enter a valid URL.'}), 400

        results = audit_seo(url)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
