from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.javascript_beautifier_utils import beautify_js

js_beautifier_bp = Blueprint('javascript_beautifier', __name__, url_prefix='/tools/js-beautifier')

@js_beautifier_bp.route('/', methods=['GET'])
def js_beautifier():
    return render_template('tools/javascript_beautifier.html', csrf_token=generate_csrf())

@js_beautifier_bp.route('/ajax', methods=['POST'])
def js_beautifier_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        raw_code = request.form.get("code", "").strip()
        if not raw_code:
            return jsonify({'error': 'Please paste JavaScript code to beautify.'}), 400

        result = beautify_js(raw_code)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
