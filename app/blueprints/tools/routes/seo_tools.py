"""
SEO Tools Routes - Modular SEO functionality
Handles all SEO-related tools including audit, reports, and analysis
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf, validate_csrf, CSRFProtect
from werkzeug.exceptions import BadRequest
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


@seo_tools_bp.route("/")
def seo_tools_index():
    """SEO tools category index"""
    user_has_pro = is_premium_user()

    category = {
        "name": "SEO Tools",
        "description": "Professional SEO analysis and optimization tools for better search rankings",
        "tools": [
            {
                "name": "SEO Audit Tool",
                "slug": "audit-tool",
                "description": "Free: 1 audit/day with basic overview. Premium: Unlimited with full analysis",
                "features": [
                    "✅ Free: Basic SEO audit (50+ checks)",
                    "✅ Free: Core Web Vitals monitoring",
                    "✅ Free: Technical SEO overview",
                    "🔒 Premium: Advanced competitor analysis",
                    "🔒 Premium: ROI forecasting & business impact",
                    "🔒 Premium: Local SEO & schema markup",
                    "🔒 Premium: Content gap analysis",
                    "🔒 Premium: Backlink profile analysis",
                    "🔒 Premium: White-label PDF reports",
                    "🔒 Premium: API access & integrations",
                    "🔒 Premium: Unlimited daily usage",
                    "🔒 Premium: Priority support",
                ],
                "is_premium": False,  # Accessible to free users with limitations
                "is_working": True,  # This tool actually works
            },
            {
                "name": "Rank Tracker",
                "slug": "rank-tracker",
                "description": "Track keyword rankings and monitor progress",
                "features": [
                    "Keyword tracking",
                    "Position monitoring",
                    "Historical data",
                ],
                "is_premium": True,
                "is_working": False,
            },
            {
                "name": "Competitor Analysis",
                "slug": "competitor-analysis",
                "description": "Analyze competitor strategies and find opportunities",
                "features": [
                    "Competitor insights",
                    "Gap analysis",
                    "Strategy recommendations",
                ],
                "is_premium": True,
                "is_working": False,
            },
        ],
    }

    return render_template(
        "tools/seo_category_index.html", category=category, user_has_pro=user_has_pro
    )


@seo_tools_bp.route("/audit-tool")
def seo_audit_tool():
    """SEO Audit Tool - Main interface"""
    user_has_pro = is_premium_user()

    # Usage tracking for free users
    usage_info = {"usage_count": 0, "limit": 1, "period": "day"}
    usage_message = "Free users get 1 SEO audit per day with basic overview"

    if not user_has_pro and current_user.is_authenticated:
        # TODO: Implement actual usage tracking from database
        # For now, using placeholder values
        from datetime import datetime, timedelta
        from app.models.user import User
        from app.core.extensions import db

        # Check daily usage (placeholder - implement with actual database tracking)
        today = datetime.now().date()
        # In real implementation, query user's audit history for today
        daily_audits = 0  # Get from database: AuditHistory.query.filter_by(user_id=current_user.id, date=today).count()

        usage_info = {"usage_count": daily_audits, "limit": 1, "period": "day"}
        usage_message = (
            f"Free users: {daily_audits}/1 daily audit used (Basic overview only)"
        )

        if daily_audits >= 1:
            usage_message = "Daily limit reached. Upgrade to Premium for unlimited audits with full analysis"
    elif not current_user.is_authenticated:
        usage_message = "Sign up for 1 free audit per day, or upgrade to Premium for unlimited access"

    return render_template(
        "tools/seo_audit_tool.html",
        tool={
            "name": "SEO Audit Tool",
            "description": "Comprehensive SEO analysis with premium features",
            "is_premium": False,  # Tool is accessible to all, but features vary
            "category": "SEO Tools",
            "features": [
                "Advanced Technical SEO Analysis (200+ checks)",
                "Complete On-page Optimization Review",
                "Core Web Vitals & Performance Metrics",
                (
                    "Premium: Competitor Intelligence & Market Analysis"
                    if user_has_pro
                    else "Basic Analysis (Upgrade for Competitor Intelligence)"
                ),
                (
                    "Premium: Content Gap Analysis & Strategy"
                    if user_has_pro
                    else "Upgrade for Content Strategy Insights"
                ),
                (
                    "Premium: Backlink Profile & Authority Analysis"
                    if user_has_pro
                    else "Upgrade for Backlink Analysis"
                ),
                (
                    "Premium: Local SEO & Schema Markup Analysis"
                    if user_has_pro
                    else "Upgrade for Local SEO Features"
                ),
                (
                    "Premium: ROI Forecasting & Business Impact"
                    if user_has_pro
                    else "Upgrade for ROI Analysis"
                ),
                (
                    "Premium: White-label PDF Reports"
                    if user_has_pro
                    else "Upgrade for Professional Reports"
                ),
                (
                    "Premium: API Access & Integrations"
                    if user_has_pro
                    else "Upgrade for API Access"
                ),
            ],
        },
        user_has_pro=user_has_pro,
        is_premium=user_has_pro,  # Add this for template compatibility
        usage_info=usage_info,  # Add usage information
        usage_message=usage_message,  # Add usage message
        user_is_authenticated=current_user.is_authenticated,
        csrf_token=generate_csrf(),  # Add CSRF token for form security
    )


@seo_tools_bp.route("/audit-tool/test", methods=["GET"])
def test_seo_audit():
    """Test endpoint for SEO audit functionality"""
    try:
        # Test with a simple URL
        test_url = "https://google.com"
        result = audit_seo(test_url, is_premium=False)
        return jsonify({"test": "success", "result": result})
    except Exception as e:
        return jsonify({"test": "failed", "error": str(e)}), 500


@seo_tools_bp.route("/api/analyze", methods=["POST"])
def api_analyze_seo():
    """API endpoint for SEO analysis without CSRF protection"""
    try:
        # Get URL from request (both form and JSON supported)
        if request.is_json:
            data = request.get_json()
            url = data.get("url", "").strip()
        else:
            url = request.form.get("url", "").strip()

        if not url:
            return jsonify({"success": False, "error": "URL is required"}), 400

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        print(f"DEBUG API: Processing URL: {url}")

        # Check if user has premium access
        user_is_premium = is_premium_user()

        # Allow both authenticated and unauthenticated users to use free version
        if not user_is_premium:
            if current_user.is_authenticated:
                # TODO: Implement actual database check for daily usage
                # For registered users, allow 3 audits per day
                from datetime import datetime

                today = datetime.now().date()
                # daily_audits = AuditHistory.query.filter_by(user_id=current_user.id, date=today).count()
                daily_audits = 0  # Placeholder

                if daily_audits >= 3:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Daily limit reached. Upgrade to Premium for unlimited audits.",
                                "upgrade_required": True,
                            }
                        ),
                        429,
                    )
            # Unauthenticated users get 1 free audit per session - no restrictions for now

        # Perform SEO audit with premium/free differentiation
        audit_results = audit_seo(url, is_premium=user_is_premium)

        if audit_results.get("success"):
            # TODO: Save audit to database for usage tracking
            # AuditHistory.create(user_id=current_user.id, url=url, results=audit_results)

            return jsonify(audit_results)
        else:
            return jsonify(audit_results), 400

    except Exception as e:
        print(f"DEBUG API: Error - {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"}), 500


@seo_tools_bp.route("/audit-tool/analyze", methods=["POST", "GET"])
def analyze_seo():
    """Perform SEO analysis - Premium vs Free differentiation"""
    try:
        # Handle both GET and POST for testing
        if request.method == "GET":
            url = request.args.get("url", "google.com")
        else:
            # Skip CSRF validation for now to test functionality
            url = request.form.get("url", "").strip()

        if not url:
            return jsonify({"success": False, "error": "URL is required"}), 400

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        print(f"DEBUG: Processing URL: {url}")

        # Check if user has premium access
        user_is_premium = is_premium_user()

        # For free users, check daily limit
        if not user_is_premium:
            if current_user.is_authenticated:
                # TODO: Implement actual database check for daily usage
                # For now, using placeholder logic
                from datetime import datetime

                today = datetime.now().date()
                # daily_audits = AuditHistory.query.filter_by(user_id=current_user.id, date=today).count()
                daily_audits = 0  # Placeholder

                if daily_audits >= 1:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Daily limit reached. Upgrade to Premium for unlimited audits.",
                                "upgrade_required": True,
                            }
                        ),
                        429,
                    )
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Please sign up for free daily audit or upgrade to Premium",
                            "login_required": True,
                        }
                    ),
                    401,
                )

        # Perform SEO audit with premium/free differentiation
        audit_results = audit_seo(url, is_premium=user_is_premium)

        if audit_results.get("success"):
            # TODO: Save audit to database for usage tracking
            # AuditHistory.create(user_id=current_user.id, url=url, results=audit_results)

            return jsonify(audit_results)
        else:
            return jsonify(audit_results), 400

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
