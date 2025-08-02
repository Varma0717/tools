from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.javascript_minifier_utils import minify_js

js_minifier_bp = Blueprint('javascript_minifier', __name__, url_prefix='/tools/js-minifier')

@js_minifier_bp.route('/', methods=['GET'])
def js_minifier():
    return render_template('tools/javascript_minifier.html', csrf_token=generate_csrf())

@js_minifier_bp.route('/ajax', methods=['POST'])
def js_minifier_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        raw_code = request.form.get("code", "").strip()
        if not raw_code:
            return jsonify({'error': 'Please paste JavaScript code to minify.'}), 400

        result = minify_js(raw_code)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
