from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.internal_link_structure_analyzer_utils import analyze_internal_structure

internal_link_structure_analyzer_bp = Blueprint('internal_link_structure_analyzer', __name__, url_prefix='/tools/internal-link-structure')

@internal_link_structure_analyzer_bp.route('/', methods=['GET'])
def internal_link_structure():
    return render_template('tools/internal_link_structure_analyzer.html', csrf_token=generate_csrf())

@internal_link_structure_analyzer_bp.route('/ajax', methods=['POST'])
def internal_link_structure_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        url = request.form.get("url", "").strip()
        if not url:
            return jsonify({'error': 'Please enter a valid URL.'}), 400

        results = analyze_internal_structure(url)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
