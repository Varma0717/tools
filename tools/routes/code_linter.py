from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.code_linter_utils import lint_html, lint_css, lint_js

code_linter_bp = Blueprint('code_linter', __name__, url_prefix='/tools/code-linter')

@code_linter_bp.route('/', methods=['GET'])
def code_linter():
    return render_template('tools/code_linter.html', csrf_token=generate_csrf())

@code_linter_bp.route('/ajax', methods=['POST'])
def code_linter_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        code = request.form.get("code", "").strip()
        mode = request.form.get("mode", "").strip()

        if not code or mode not in ["html", "css", "js"]:
            return jsonify({'error': 'Please provide valid code and mode (html, css, js).'}), 400

        if mode == "html":
            results = lint_html(code)
        elif mode == "css":
            results = lint_css(code)
        else:
            results = lint_js(code)

        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
