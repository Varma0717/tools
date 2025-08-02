from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.css_js_bundler_utils import bundle_files

bundler_bp = Blueprint('css_js_bundler', __name__, url_prefix='/tools/bundler')

@bundler_bp.route('/')
def css_js_bundler():
    return render_template('tools/css_js_bundler.html', csrf_token=generate_csrf())

@bundler_bp.route('/ajax', methods=['POST'])
def css_js_bundler_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        code1 = request.form.get("code1", "").strip()
        code2 = request.form.get("code2", "").strip()
        code3 = request.form.get("code3", "").strip()
        mode = request.form.get("mode", "").strip()

        if not any([code1, code2, code3]):
            return jsonify({"error": "Please paste at least one file."}), 400

        bundled, error = bundle_files([code1, code2, code3], mode)
        if error:
            return jsonify({"error": error}), 500
        return jsonify({"result": bundled})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
