from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
from app.blueprints.tools.utils.seo_audit_tool_utils import audit_seo
import logging

seo_audit_tool_bp = Blueprint("seo_audit_tool", __name__, url_prefix="/tools")
logger = logging.getLogger(__name__)


@seo_audit_tool_bp.route("/seo-audit-tool", methods=["GET"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def seo_audit():
    """SEO Audit Tool - Comprehensive website analysis"""
    csrf_token = generate_csrf()
    return render_template("tools/seo_audit_tool.html", csrf_token=csrf_token)


@seo_audit_tool_bp.route("/seo-audit-tool/analyze", methods=["POST"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def seo_audit_analyze():
    """SEO Audit Analysis - Comprehensive website analysis"""
    try:
        url = request.form.get("url", "").strip()
        if not url:
            return (
                jsonify({"success": False, "error": "Please enter a valid URL."}),
                400,
            )

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Perform comprehensive SEO audit using existing utility
        results = audit_seo(url)

        if results.get("success"):
            return jsonify({"success": True, "data": results})
        else:
            return (
                jsonify(
                    {"success": False, "error": results.get("error", "Analysis failed")}
                ),
                500,
            )

    except Exception as e:
        logger.error(f"SEO audit error: {str(e)}")
        return (
            jsonify({"success": False, "error": "An error occurred during analysis."}),
            500,
        )
