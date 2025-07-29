from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
from app.blueprints.tools.utils.advanced_keyword_research_utils import analyze_keywords

advanced_keyword_research_bp = Blueprint(
    "advanced_keyword_research", __name__, url_prefix="/tools"
)


@advanced_keyword_research_bp.route("/advanced-keyword-research/", methods=["GET"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def advanced_keyword_research():
    """Advanced keyword research tool with comprehensive analysis"""
    csrf_token = generate_csrf()
    return render_template(
        "tools/advanced_keyword_research.html",
        csrf_token=csrf_token,
        csrf_token=generate_csrf(),
    )


@advanced_keyword_research_bp.route("/advanced-keyword-research/ajax", methods=["POST"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def advanced_keyword_research_ajax():
    """AJAX endpoint for advanced keyword analysis"""
    try:
        data = request.get_json() or {}
        keyword = data.get("keyword", "").strip()
        location = data.get("location", "United States").strip()
        language = data.get("language", "en").strip()
        analysis_type = data.get("analysis_type", "comprehensive").strip()

        if not keyword:
            return (
                jsonify(
                    {"success": False, "error": "Please enter a keyword to analyze."}
                ),
                400,
            )

        # Check if user is premium for advanced features
        user_type = data.get("user_type", "free")

        results = analyze_keywords(
            keyword=keyword,
            location=location,
            language=language,
            analysis_type=analysis_type,
            user_type=user_type,
        )

        if results.get("success"):
            return jsonify(results)
        else:
            return (
                jsonify(
                    {"success": False, "error": results.get("error", "Analysis failed")}
                ),
                400,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@advanced_keyword_research_bp.route("/advanced-keyword-research/")
def advanced_keyword_research_page():
    """Advanced Keyword Research main page."""
    return render_template("tools/advanced_keyword_research.html", csrf_token=generate_csrf())
