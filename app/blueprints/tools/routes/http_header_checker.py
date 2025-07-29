from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from app.blueprints.tools.utils.http_header_checker_utils import check_http_headers

http_header_checker_bp = Blueprint('http_header_checker', __name__, url_prefix='/tools/http-header-checker')

@http_header_checker_bp.route('/')
def http_header_checker():
    return render_template('tools/http_header_checker.html', csrf_token=generate_csrf())

@http_header_checker_bp.route('/ajax', methods=['POST'])
def http_header_checker_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        url = request.form.get("url", "").strip()
        if not url:
            return jsonify({"error": "Please enter a valid URL."}), 400

        headers, error = check_http_headers(url)
        if error:
            return jsonify({"error": error}), 500
        return jsonify({"headers": headers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@http_header_checker_bp.route("/http-header-checker/")
def http_header_checker_page():
    """Http Header Checker main page."""
    return render_template("tools/http_header_checker.html", csrf_token=generate_csrf())
