from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from flask_login import login_required, current_user, logout_user, login_user
from tools.utils.auto_title_generator_utils import generate_auto_titles

auto_title_generator_bp = Blueprint(
    "auto_title_generator", __name__, url_prefix="/tools/auto-title-generator"
)


@auto_title_generator_bp.route("/", methods=["GET"])
@login_required
def auto_title_generator():
    return render_template(
        "tools/auto_title_generator.html", csrf_token=generate_csrf()
    )


@auto_title_generator_bp.route("/ajax", methods=["POST"])
def auto_title_generator_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        keyword = request.form.get("keyword", "").strip()
        if not keyword:
            return jsonify({"error": "Please enter a keyword or phrase."}), 400

        result, error = generate_auto_titles(keyword)
        if error:
            return jsonify({"error": error}), 500

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
