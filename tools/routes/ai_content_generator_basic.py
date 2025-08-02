from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf, CSRFProtect
from flask_login import login_required, current_user, logout_user, login_user
from tools.utils.ai_content_generator_basic_utils import generate_ai_content

csrf = CSRFProtect()

ai_content_generator_basic_bp = Blueprint(
    "ai_content_generator_basic", __name__, url_prefix="/tools/ai-content-generator"
)


@ai_content_generator_basic_bp.route("/", methods=["GET"])
@login_required
@csrf.exempt
def ai_content_generator():
    return render_template(
        "tools/ai_content_generator_basic.html", csrf_token=generate_csrf()
    )


@ai_content_generator_basic_bp.route("/ajax", methods=["POST"])
def ai_content_generator_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        topic = request.form.get("topic", "").strip()
        desc = request.form.get("desc", "").strip()

        if not topic:
            return jsonify({"error": "Please enter a topic."}), 400

        result, error = generate_ai_content(topic, desc)
        if error:
            return jsonify({"error": error}), 500

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
