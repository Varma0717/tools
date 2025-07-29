from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
from app.blueprints.tools.utils.technical_seo_analyzer_utils import (
    analyze_technical_seo,
)

technical_seo_analyzer_bp = Blueprint(
    "technical_seo_analyzer", __name__, url_prefix="/tools"
)


@technical_seo_analyzer_bp.route("/technical-seo-analyzer", methods=["GET"])
@freemium_tool(requires_login=True, is_premium=True, free_limit=0)
def technical_seo_analyzer():
    """Advanced technical SEO analyzer with comprehensive website analysis"""
    csrf_token = generate_csrf()
    return render_template("tools/technical_seo_analyzer.html", csrf_token=csrf_token)


@technical_seo_analyzer_bp.route("/technical-seo-analyzer/ajax", methods=["POST"])
@freemium_tool(requires_login=True, is_premium=True, free_limit=0)
def technical_seo_analyzer_ajax():
    """AJAX endpoint for technical SEO analysis"""
    try:
        data = request.get_json() or {}
        url = data.get("url", "").strip()
        analysis_depth = data.get("analysis_depth", "standard").strip()
        include_mobile = data.get("include_mobile", True)
        check_performance = data.get("check_performance", True)

        if not url:
            return (
                jsonify(
                    {"success": False, "error": "Please enter a valid URL to analyze."}
                ),
                400,
            )

        # Check if user is premium for advanced features
        user_type = data.get("user_type", "free")

        results = analyze_technical_seo(
            url=url,
            analysis_depth=analysis_depth,
            include_mobile=include_mobile,
            check_performance=check_performance,
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


@technical_seo_analyzer_bp.route("/technical-seo-analyzer/")
def technical_seo_analyzer_page():
    """Technical Seo Analyzer main page."""
    return render_template("tools/technical_seo_analyzer.html", csrf_token=generate_csrf())
