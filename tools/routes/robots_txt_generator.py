from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.robots_txt_generator_utils import generate_robots_txt

robots_bp = Blueprint('robots_generator', __name__, url_prefix='/tools/robots-generator')

@robots_bp.route('/')
def robots_generator():
    return render_template('tools/robots_generator.html', csrf_token=generate_csrf())

@robots_bp.route('/ajax', methods=['POST'])
def robots_generator_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        form_data = {
            "agent": request.form.get("agent", "*"),
            "allow": request.form.get("allow", ""),
            "disallow": request.form.get("disallow", ""),
            "sitemap": request.form.get("sitemap", ""),
            "crawl_delay": request.form.get("crawl_delay", "")
        }

        result, error = generate_robots_txt(form_data)
        if error:
            return jsonify({"error": error}), 500

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
