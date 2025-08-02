"""
SEO Analysis Routes
Advanced SEO analysis endpoints with comprehensive reporting
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import json

from utils.seo_analyzer import SEOAnalyzer, analyze_url_seo, bulk_analyze_urls
from utils.caching import cached
from utils.decorators import rate_limit

# Create blueprint for SEO analysis
seo_bp = Blueprint("seo", __name__, url_prefix="/seo")


@seo_bp.route("/")
@login_required
def seo_home():
    """SEO analysis home page"""
    return render_template("seo/index.html")


@seo_bp.route("/analyze")
@login_required
def analyze_page():
    """Single URL analysis page"""
    return render_template("seo/analyze.html")


@seo_bp.route("/bulk-analyze")
@login_required
def bulk_analyze_page():
    """Bulk URL analysis page"""
    return render_template("seo/bulk_analyze.html")


@seo_bp.route("/api/analyze", methods=["POST"])
@login_required
@rate_limit(max_requests=20, window=3600, per="user")  # 20 per hour
def api_analyze():
    """API endpoint for single URL analysis"""
    try:
        data = request.get_json()

        if not data or "url" not in data:
            return jsonify({"error": "URL is required", "status": "error"}), 400

        url = data["url"].strip()
        deep_analysis = data.get("deep_analysis", False)

        # Validate URL format
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Perform SEO analysis
        result = analyze_url_seo(url, deep_analysis)

        # Log analysis for user
        if current_user and result.get("status") == "success":
            # Here you could log the analysis to database for history
            pass

        return jsonify(
            {
                "status": "success",
                "data": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@seo_bp.route("/api/bulk-analyze", methods=["POST"])
@login_required
@rate_limit(max_requests=5, window=3600, per="user")  # 5 bulk analyses per hour
def api_bulk_analyze():
    """API endpoint for bulk URL analysis"""
    try:
        data = request.get_json()

        if not data or "urls" not in data:
            return jsonify({"error": "URLs list is required", "status": "error"}), 400

        urls = data["urls"]
        deep_analysis = data.get("deep_analysis", False)

        # Validate URLs
        if not isinstance(urls, list) or len(urls) == 0:
            return (
                jsonify({"error": "URLs must be a non-empty list", "status": "error"}),
                400,
            )

        if len(urls) > 10:  # Limit bulk analysis
            return (
                jsonify(
                    {
                        "error": "Maximum 10 URLs allowed for bulk analysis",
                        "status": "error",
                    }
                ),
                400,
            )

        # Clean URLs
        cleaned_urls = []
        for url in urls:
            url = url.strip()
            if url:
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                cleaned_urls.append(url)

        # Perform bulk analysis
        results = bulk_analyze_urls(cleaned_urls, deep_analysis)

        return jsonify(
            {
                "status": "success",
                "data": results,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@seo_bp.route("/api/quick-score", methods=["POST"])
@login_required
@rate_limit(max_requests=50, window=3600, per="user")  # 50 quick checks per hour
def api_quick_score():
    """Quick SEO score check (cached, lightweight analysis)"""
    try:
        data = request.get_json()

        if not data or "url" not in data:
            return jsonify({"error": "URL is required", "status": "error"}), 400

        url = data["url"].strip()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Use cached lightweight analysis
        @cached(ttl=1800, key_func=lambda u: f"quick_seo:{u}")  # 30 min cache
        def get_quick_score(url):
            analyzer = SEOAnalyzer()
            # Perform basic analysis only
            result = analyzer.analyze_url(url, deep_analysis=False)

            # Return simplified result
            return {
                "url": url,
                "overall_score": result.get("overall_score", 0),
                "status": result.get("summary", {}).get("status", "unknown"),
                "top_issues": result.get("recommendations", [])[:3],
                "cached": result.get("cached", False),
                "timestamp": result.get("timestamp"),
            }

        result = get_quick_score(url)

        return jsonify(
            {
                "status": "success",
                "data": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@seo_bp.route("/history")
@login_required
def analysis_history():
    """User's SEO analysis history"""
    # This would show user's analysis history from database
    return render_template("seo/history.html")


@seo_bp.route("/report/<analysis_id>")
@login_required
def view_report(analysis_id):
    """View detailed SEO analysis report"""
    # This would load a specific analysis report
    return render_template("seo/report.html", analysis_id=analysis_id)


@seo_bp.route("/api/export/<analysis_id>")
@login_required
def export_report(analysis_id):
    """Export SEO analysis report as PDF/JSON"""
    # This would export the analysis report
    return jsonify({"status": "success", "message": "Export functionality coming soon"})


# Template filters for SEO analysis
@seo_bp.app_template_filter("seo_score_color")
def seo_score_color(score):
    """Get color class for SEO score"""
    if score >= 80:
        return "success"
    elif score >= 60:
        return "warning"
    elif score >= 40:
        return "info"
    else:
        return "danger"


@seo_bp.app_template_filter("seo_score_text")
def seo_score_text(score):
    """Get text description for SEO score"""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Poor"


def register_seo_routes(app):
    """Register SEO analysis routes with the app"""
    app.register_blueprint(seo_bp)

    # Add SEO tools to main navigation
    if not hasattr(app, "main_menu_items"):
        app.main_menu_items = []

    app.main_menu_items.extend(
        [
            {
                "name": "SEO Analyzer",
                "url": "seo.analyze_page",
                "icon": "fas fa-search",
                "order": 2,
            },
            {
                "name": "Bulk Analysis",
                "url": "seo.bulk_analyze_page",
                "icon": "fas fa-list-ul",
                "order": 3,
            },
        ]
    )
