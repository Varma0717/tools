from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
from app.blueprints.tools.utils.seo_audit_tool_utils import audit_seo
import logging
import re

seo_audit_tool_bp = Blueprint("seo_audit_tool", __name__, url_prefix="/tools")
logger = logging.getLogger(__name__)


def is_valid_url(url):
    """Basic URL validation"""
    if not url:
        return False

    # Simple URL pattern check
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return bool(url_pattern.match(url))


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
        url = request.form.get("primary_input", "").strip()
        if not url:
            return (
                jsonify({"success": False, "error": "Please enter a valid URL."}),
                400,
            )

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Validate URL format
        if not is_valid_url(url):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Please enter a valid URL format (e.g., https://example.com)",
                    }
                ),
                400,
            )

        logger.info(f"Starting SEO audit for URL: {url}")

        # Perform comprehensive SEO audit using existing utility
        results = audit_seo(url)

        # Check if results contain error or if audit was successful
        if results.get("success") is False:
            error_msg = results.get("error", "Analysis failed")
            logger.error(f"SEO audit failed for {url}: {error_msg}")
            return (
                jsonify({"success": False, "error": error_msg}),
                500,
            )
        else:
            # Audit completed successfully
            logger.info(f"SEO audit completed successfully for {url}")
            return jsonify({"success": True, "result": results})

    except Exception as e:
        logger.error(f"SEO audit error: {str(e)}")
        return (
            jsonify({"success": False, "error": "An error occurred during analysis."}),
            500,
        )
