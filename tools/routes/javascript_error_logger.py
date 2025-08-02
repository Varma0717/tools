from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.javascript_error_logger_utils import log_js_errors

js_error_logger_bp = Blueprint('js_error_logger', __name__, url_prefix='/tools/javascript-error-logger')

@js_error_logger_bp.route('/')
def js_error_logger():
    return render_template('tools/javascript_error_logger.html', csrf_token=generate_csrf())

@js_error_logger_bp.route('/ajax', methods=['POST'])
def js_error_logger_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        code = request.form.get("code", "")
        if not code.strip():
            return jsonify({"error": "Please paste some JavaScript code."}), 400

        results, error = log_js_errors(code)
        if error:
            return jsonify({"error": error}), 500
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
