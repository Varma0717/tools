from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
from app.blueprints.tools.utils.seo_audit_tool_utils import audit_seo

seo_audit_tool_bp = Blueprint("seo_audit_tool", __name__, url_prefix="/tools")


@seo_audit_tool_bp.route("/seo-audit-tool", methods=["GET"])
@freemium_tool(requires_login=True, is_premium=True, free_limit=0)
def seo_audit():
    csrf_token = generate_csrf()
    return render_template("tools/seo_audit_tool.html", csrf_token=csrf_token)


@seo_audit_tool_bp.route("/seo-audit-tool/ajax", methods=["POST"])
@freemium_tool(requires_login=True, is_premium=True, free_limit=0)
def seo_audit_ajax():
    try:
        url = request.form.get("url", "").strip()
        if not url:
            return (
                jsonify({"success": False, "error": "Please enter a valid URL."}),
                400,
            )

        results = audit_seo(url)

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


@seo_audit_tool_bp.route("/seo-audit-tool/")
def seo_audit_tool_page():
    """Seo Audit Tool main page."""
    return render_template("tools/seo_audit_tool.html", csrf_token=generate_csrf())
