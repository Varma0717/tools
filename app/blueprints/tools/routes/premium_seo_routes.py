"""
Premium SEO Routes - Advanced features for Pro users
Competitor analysis, historical tracking, and advanced insights
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json

# Import database
from app.core.extensions import db
from ..utils.premium_seo_features import PremiumSEOFeatures

# Create premium SEO blueprint
premium_seo_bp = Blueprint("premium_seo", __name__, url_prefix="/tools/seo/premium")


def require_premium():
    """Decorator to ensure user has premium access"""

    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_pro_user():
                flash("Premium features require a Pro subscription.", "warning")
                return redirect(url_for("seo_tools.seo_tools_index"))
            return f(*args, **kwargs)

        decorated_function.__name__ = f.__name__
        return decorated_function

    return decorator


@premium_seo_bp.route("/")
@login_required
@require_premium()
def premium_dashboard():
    """Premium SEO dashboard with advanced features"""
    return render_template(
        "tools/premium_seo_dashboard.html",
        user=current_user,
        page_title="Premium SEO Dashboard",
    )


@premium_seo_bp.route("/competitor-analysis", methods=["GET", "POST"])
@login_required
@require_premium()
def competitor_analysis():
    """Analyze competitors for benchmarking"""
    if request.method == "POST":
        data = request.get_json()
        website_url = data.get("url", "").strip()
        competitor_urls = data.get("competitors", [])

        if not website_url:
            return jsonify({"success": False, "error": "Website URL is required"})

        try:
            premium_features = PremiumSEOFeatures(website_url, current_user.id)

            # Run competitor analysis
            competitor_data = premium_features.analyze_competitors(competitor_urls)

            return jsonify(
                {
                    "success": True,
                    "analysis": competitor_data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            return jsonify(
                {"success": False, "error": f"Competitor analysis failed: {str(e)}"}
            )

    return render_template(
        "tools/competitor_analysis.html",
        user=current_user,
        page_title="Competitor Analysis",
    )


@premium_seo_bp.route("/historical-tracking", methods=["GET", "POST"])
@login_required
@require_premium()
def historical_tracking():
    """Track SEO metrics over time"""
    if request.method == "POST":
        data = request.get_json()
        website_url = data.get("url", "").strip()
        days_back = int(data.get("days", 30))

        if not website_url:
            return jsonify({"success": False, "error": "Website URL is required"})

        try:
            premium_features = PremiumSEOFeatures(website_url, current_user.id)

            # Get historical tracking data
            historical_data = premium_features.historical_tracking(days_back)

            return jsonify(
                {
                    "success": True,
                    "tracking": historical_data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            return jsonify(
                {"success": False, "error": f"Historical tracking failed: {str(e)}"}
            )

    return render_template(
        "tools/historical_tracking.html",
        user=current_user,
        page_title="Historical SEO Tracking",
    )


@premium_seo_bp.route("/keyword-analysis", methods=["GET", "POST"])
@login_required
@require_premium()
def advanced_keyword_analysis():
    """Advanced keyword analysis and opportunities"""
    if request.method == "POST":
        data = request.get_json()
        website_url = data.get("url", "").strip()

        if not website_url:
            return jsonify({"success": False, "error": "Website URL is required"})

        try:
            premium_features = PremiumSEOFeatures(website_url, current_user.id)

            # Run advanced keyword analysis
            keyword_data = premium_features.advanced_keyword_analysis()

            return jsonify(
                {
                    "success": True,
                    "keywords": keyword_data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            return jsonify(
                {"success": False, "error": f"Keyword analysis failed: {str(e)}"}
            )

    return render_template(
        "tools/keyword_analysis.html",
        user=current_user,
        page_title="Advanced Keyword Analysis",
    )


@premium_seo_bp.route("/bulk-analysis", methods=["GET", "POST"])
@login_required
@require_premium()
def bulk_analysis():
    """Bulk SEO analysis for multiple URLs"""
    if request.method == "POST":
        data = request.get_json()
        urls = data.get("urls", [])

        if not urls or len(urls) == 0:
            return jsonify({"success": False, "error": "At least one URL is required"})

        if len(urls) > 10:
            return jsonify(
                {"success": False, "error": "Maximum 10 URLs allowed per bulk analysis"}
            )

        try:
            from ..utils.enhanced_seo_analyzer import ComprehensiveSEOAnalyzer

            bulk_results = []

            for url in urls:
                try:
                    analyzer = ComprehensiveSEOAnalyzer(url.strip(), is_premium=True)
                    result = analyzer.analyze()

                    bulk_results.append(
                        {
                            "url": url,
                            "success": result.get("success", False),
                            "overall_score": result.get("overall_score", 0),
                            "score_breakdown": result.get("score_breakdown", {}),
                            "critical_issues": len(
                                result.get("recommendations", {}).get("critical", [])
                            ),
                            "total_issues": sum(
                                len(items)
                                for items in result.get("recommendations", {}).values()
                                if isinstance(items, list)
                            ),
                        }
                    )

                except Exception as e:
                    bulk_results.append({"url": url, "success": False, "error": str(e)})

            return jsonify(
                {
                    "success": True,
                    "results": bulk_results,
                    "summary": {
                        "total_analyzed": len(bulk_results),
                        "successful": len(
                            [r for r in bulk_results if r.get("success")]
                        ),
                        "failed": len(
                            [r for r in bulk_results if not r.get("success")]
                        ),
                        "average_score": round(
                            sum(
                                r.get("overall_score", 0)
                                for r in bulk_results
                                if r.get("success")
                            )
                            / max(
                                1, len([r for r in bulk_results if r.get("success")])
                            ),
                            2,
                        ),
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            return jsonify(
                {"success": False, "error": f"Bulk analysis failed: {str(e)}"}
            )

    return render_template(
        "tools/bulk_analysis.html", user=current_user, page_title="Bulk SEO Analysis"
    )


@premium_seo_bp.route("/api/features")
@login_required
@require_premium()
def get_premium_features():
    """Get available premium features"""
    features = {
        "competitor_analysis": {
            "name": "Competitor Analysis",
            "description": "Compare your SEO performance against competitors",
            "endpoint": "/tools/seo/premium/competitor-analysis",
        },
        "historical_tracking": {
            "name": "Historical Tracking",
            "description": "Track SEO progress over time with trend analysis",
            "endpoint": "/tools/seo/premium/historical-tracking",
        },
        "keyword_analysis": {
            "name": "Advanced Keywords",
            "description": "Deep keyword analysis and optimization opportunities",
            "endpoint": "/tools/seo/premium/keyword-analysis",
        },
        "bulk_analysis": {
            "name": "Bulk Analysis",
            "description": "Analyze multiple URLs simultaneously",
            "endpoint": "/tools/seo/premium/bulk-analysis",
        },
    }

    return jsonify(
        {
            "success": True,
            "features": features,
            "user_id": current_user.id,
            "subscription_status": "active",
        }
    )
