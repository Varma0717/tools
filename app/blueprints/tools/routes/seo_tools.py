"""
SEO Tools Routes - Modular SEO functionality
Handles all SEO-related tools including audit, reports, and analysis
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import time
import json
from datetime import datetime

# Import SEO utilities
from ..utils.seo_audit_tool_utils import audit_seo
from ..utils.advanced_seo_analyzer import PremiumSEOAnalyzer

# Create SEO tools blueprint
seo_tools_bp = Blueprint("seo_tools", __name__, url_prefix="/tools/seo")


def is_premium_user():
    """Check if current user has premium access"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_pro_user()


@seo_tools_bp.route("/audit-tool")
def seo_audit_tool():
    """SEO Audit Tool - Main interface"""
    user_has_pro = is_premium_user()

    return render_template(
        "tools/seo_audit_tool.html",
        tool={
            "name": "SEO Audit Tool",
            "description": "Comprehensive SEO analysis with premium features",
            "is_premium": False,  # Tool is accessible to all, but features vary
            "category": "SEO Tools",
            "features": [
                "Technical SEO Analysis",
                "On-page Optimization Checks",
                "Performance Metrics",
                (
                    "Premium: 150+ Advanced Checks"
                    if user_has_pro
                    else "Basic Analysis (Upgrade for 150+ Checks)"
                ),
                (
                    "Premium: Competitor Analysis"
                    if user_has_pro
                    else "Upgrade for Competitor Analysis"
                ),
                (
                    "Premium: Advanced Reporting"
                    if user_has_pro
                    else "Upgrade for Advanced Reports"
                ),
            ],
        },
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )


@seo_tools_bp.route("/audit-tool/analyze", methods=["POST"])
def analyze_seo():
    """Perform SEO analysis - Premium vs Free differentiation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        url = data.get("url", "").strip()
        if not url:
            return jsonify({"success": False, "error": "URL is required"}), 400

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Check if user has premium access
        user_is_premium = is_premium_user()

        # Perform SEO audit with premium/free differentiation
        audit_results = audit_seo(url, is_premium=user_is_premium)

        if not audit_results.get("success", True):
            return jsonify(audit_results), 400

        # Add user context to results
        audit_results["user_is_premium"] = user_is_premium
        audit_results["upgrade_message"] = (
            None
            if user_is_premium
            else "Upgrade to Pro for advanced analysis with 150+ checks, competitor analysis, and detailed reporting!"
        )

        return jsonify(audit_results)

    except Exception as e:
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"}), 500


@seo_tools_bp.route("/reports")
@login_required
def seo_reports_history():
    """SEO Reports History - Premium feature"""
    if not is_premium_user():
        flash("Premium subscription required to access SEO reports history.", "warning")
        return redirect(url_for("main.pricing"))

    # TODO: Implement actual reports retrieval from database
    reports = []  # Placeholder for now

    return render_template(
        "tools/seo_reports_history.html",
        reports=reports,
        user_has_pro=True,
        user_is_authenticated=True,
    )


@seo_tools_bp.route("/report/<report_id>")
@login_required
def seo_report_detail(report_id):
    """View specific SEO report - Premium feature"""
    if not is_premium_user():
        flash(
            "Premium subscription required to access detailed SEO reports.", "warning"
        )
        return redirect(url_for("main.pricing"))

    # TODO: Implement actual report retrieval from database
    report = None  # Placeholder for now

    if not report:
        flash("Report not found or you do not have access to it.", "error")
        return redirect(url_for("seo_tools.seo_reports_history"))

    return render_template(
        "tools/seo_report_detail.html",
        report=report,
        user_has_pro=True,
        user_is_authenticated=True,
    )


# Health check endpoint for SEO tools
@seo_tools_bp.route("/seo-tools/health")
def seo_tools_health():
    """Health check for SEO tools module"""
    return jsonify(
        {
            "status": "healthy",
            "module": "seo_tools",
            "timestamp": datetime.now().isoformat(),
            "routes": [
                "/seo-audit-tool",
                "/seo-audit-tool/analyze",
                "/seo-reports",
                "/seo-report/<report_id>",
            ],
        }
    )
