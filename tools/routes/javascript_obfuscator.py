from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.javascript_obfuscator_utils import obfuscate_js

js_obfuscator_bp = Blueprint('javascript_obfuscator', __name__, url_prefix='/tools/js-obfuscator')

@js_obfuscator_bp.route('/', methods=['GET'])
def js_obfuscator():
    return render_template('tools/javascript_obfuscator.html', csrf_token=generate_csrf())

@js_obfuscator_bp.route('/ajax', methods=['POST'])
def js_obfuscator_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        raw_code = request.form.get("code", "").strip()
        if not raw_code:
            return jsonify({'error': 'Please enter JavaScript code to obfuscate.'}), 400

        obfuscated = obfuscate_js(raw_code)
        return jsonify({'result': obfuscated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
