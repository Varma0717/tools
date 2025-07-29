from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError
from app.utils.auth_decorators import freemium_tool
import os
import requests

headline_generator_bp = Blueprint(
    "headline_generator", __name__, url_prefix="/tools/headline-generator"
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


@headline_generator_bp.route("/")
@freemium_tool(requires_login=True, is_premium=True, free_limit=0)
def headline_generator():
    return render_template("tools/headline_generator.html")


@headline_generator_bp.route("/ajax", methods=["POST"])
@freemium_tool(requires_login=True, is_premium=True, free_limit=0)
def headline_generator_ajax():
    try:
        csrf_token = request.headers.get("X-CSRFToken") or request.json.get(
            "csrf_token"
        )
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    data = request.get_json() or {}
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({"error": "Please enter a topic or keyword."}), 400

    prompt = (
        f"Generate 7 catchy, SEO-friendly headlines for the topic: {topic}.\nfrom flask_wtf.csrf import generate_csrf\n\nheadline_generator_bp = Blueprint("headline_generator", __name__, url_prefix="/tools")\n\n"
        "Output only the headlines as a numbered list."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.7,
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        ai_response = data["choices"][0]["message"]["content"].strip()
        return jsonify({"headlines": ai_response})
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500


@headline_generator_bp.route("/headline-generator/")
def headline_generator_page():
    """Headline Generator main page."""
    return render_template("tools/headline_generator.html", csrf_token=generate_csrf())
