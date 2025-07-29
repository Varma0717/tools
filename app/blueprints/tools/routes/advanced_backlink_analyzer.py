from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
from app.blueprints.tools.utils.advanced_backlink_analyzer_utils import (
    analyze_backlinks,
)

advanced_backlink_analyzer_bp = Blueprint(
    "advanced_backlink_analyzer", __name__, url_prefix="/tools"
)


@advanced_backlink_analyzer_bp.route("/advanced-backlink-analyzer", methods=["GET"])
@freemium_tool(requires_login=True, is_premium=False, free_limit=3)
def advanced_backlink_analyzer():
    """Advanced backlink analyzer tool with comprehensive link profile analysis"""
    csrf_token = generate_csrf()
    return render_template(
        "tools/advanced_backlink_analyzer.html", csrf_token=csrf_token
    )


@advanced_backlink_analyzer_bp.route(
    "/advanced-backlink-analyzer/ajax", methods=["POST"]
)
@freemium_tool(requires_login=True, is_premium=False, free_limit=3)
def advanced_backlink_analyzer_ajax():
    """AJAX endpoint for advanced backlink analysis"""
    try:
        data = request.get_json() or {}
        url = data.get("url", "").strip()
        analysis_type = data.get("analysis_type", "comprehensive").strip()
        include_competitors = data.get("include_competitors", False)

        if not url:
            return (
                jsonify(
                    {"success": False, "error": "Please enter a valid URL to analyze."}
                ),
                400,
            )

        # Check if user is premium for advanced features
        user_type = data.get("user_type", "free")

        results = analyze_backlinks(
            url=url,
            analysis_type=analysis_type,
            include_competitors=include_competitors,
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


@advanced_backlink_analyzer_bp.route("/advanced-backlink-analyzer/")
def advanced_backlink_analyzer_page():
    """Advanced Backlink Analyzer main page."""
    return render_template("tools/advanced_backlink_analyzer.html", csrf_token=generate_csrf())
