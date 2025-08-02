from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.html_minifier_utils import minify_html

html_minifier_bp = Blueprint('html_minifier', __name__, url_prefix='/tools/html-minifier')

@html_minifier_bp.route('/')
def html_minifier():
    return render_template('tools/html_minifier.html', csrf_token=generate_csrf())

@html_minifier_bp.route('/ajax', methods=['POST'])
def html_minifier_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        code = request.form.get("code", "").strip()

        if not code:
            return jsonify({"error": "Please enter HTML code to minify."}), 400

        result, error = minify_html(code)
        if error:
            return jsonify({"error": error}), 500

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
