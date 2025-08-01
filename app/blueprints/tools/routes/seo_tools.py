"""
SEO Tools Routes - Modular SEO functionality
Handles all SEO-related tools including audit, reports, and analysis
"""

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    make_response,
)
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf, validate_csrf, CSRFProtect
from werkzeug.exceptions import BadRequest
import time
import json
from datetime import datetime

# Import database
from app.core.extensions import db

# Import SEO utilities
from ..utils.seo_audit_tool_utils import audit_seo


def transform_enhanced_results(enhanced_results):
    """Transform enhanced analyzer results to match expected format"""
    try:
        # Extract data from enhanced results
        score_breakdown = enhanced_results.get("score_breakdown", {})
        technical_seo = enhanced_results.get("technical_seo", {})
        content_analysis = enhanced_results.get("content_analysis", {})
        performance = enhanced_results.get("performance", {})
        onpage_seo = enhanced_results.get("onpage_seo", {})
        summary = enhanced_results.get("summary", {})

        # Transform recommendations to array format (backward compatibility)
        recommendations_obj = enhanced_results.get("recommendations", {})
        if isinstance(recommendations_obj, dict):
            # Flatten categorized recommendations into a single array
            recommendations = []
            for category, recs in recommendations_obj.items():
                if isinstance(recs, list):
                    recommendations.extend(recs)
        else:
            recommendations = (
                recommendations_obj if isinstance(recommendations_obj, list) else []
            )

        # Extract detailed technical data
        technical_details = technical_seo.get("details", {})
        ssl_info = technical_details.get("ssl", {})
        robots_info = technical_details.get("robots", {})
        sitemap_info = technical_details.get("sitemap", {})

        # Extract content data from the actual enhanced analyzer format
        content_details = content_analysis.get("details", {})

        # Content analysis data is structured differently in enhanced analyzer
        titles_data = content_details.get("titles", {})
        meta_data = content_details.get("meta_descriptions", {})
        images_data = content_details.get("images", {})

        # Calculate title statistics from pages data
        title_pages = titles_data.get("pages", {})
        title_lengths = [
            page.get("length", 0) for page in title_pages.values() if page.get("exists")
        ]
        avg_title_length = (
            sum(title_lengths) / len(title_lengths) if title_lengths else 0
        )
        missing_titles = len([p for p in title_pages.values() if not p.get("exists")])

        # Calculate meta description statistics
        meta_pages = meta_data.get("pages", {})
        meta_lengths = [
            page.get("length", 0) for page in meta_pages.values() if page.get("exists")
        ]
        avg_meta_length = sum(meta_lengths) / len(meta_lengths) if meta_lengths else 0
        missing_meta = len([p for p in meta_pages.values() if not p.get("exists")])

        # Extract image data
        total_images = images_data.get("total_images", 0)
        missing_alt = images_data.get("missing_alt_tags", 0)

        # Extract performance data from the actual enhanced analyzer format
        performance_details = performance.get("details", {})
        speed_data = performance_details.get("speed", {})
        resources_data = performance_details.get("resources", {})

        # Calculate performance metrics
        avg_load_time = speed_data.get("load_time", 0)
        content_size = speed_data.get("content_size", 0)
        avg_page_size = (
            resources_data.get("total_size_mb", 0) * 1024
        )  # Convert MB to KB
        performance_details = performance.get("details", {})

        # Calculate coverage percentages
        pages_analyzed = summary.get("pages_analyzed", 1)
        https_pages = ssl_info.get(
            "https_pages", pages_analyzed if ssl_info.get("is_valid", False) else 0
        )
        pages_with_canonical = technical_details.get("canonical", {}).get(
            "pages_with_canonical", 0
        )
        pages_with_schema = technical_details.get("schema", {}).get(
            "pages_with_schema", 0
        )

        # Create compatible format with detailed analysis
        transformed = {
            "success": enhanced_results.get("success", False),
            "url": enhanced_results.get("url", ""),
            "overall_score": enhanced_results.get("overall_score", 0),
            "timestamp": enhanced_results.get("timestamp", ""),
            "total_audit_time": enhanced_results.get("audit_duration", 0),
            "is_premium_analysis": enhanced_results.get("is_premium_analysis", False),
            # Technical Analysis with detailed breakdown
            "technical_analysis": {
                "score": score_breakdown.get("technical", 0),
                "issues": technical_seo.get("issues", []),
                "details": {
                    # HTTPS Analysis
                    "https_pages": https_pages,
                    "total_pages": pages_analyzed,
                    "https_coverage": round(
                        (https_pages / max(pages_analyzed, 1)) * 100, 1
                    ),
                    # SSL Certificate
                    "ssl_status": (
                        "Valid" if ssl_info.get("is_valid", False) else "Invalid"
                    ),
                    "ssl_details": ssl_info,
                    # Canonical Tags
                    "canonical_pages": pages_with_canonical,
                    "canonical_coverage": round(
                        (pages_with_canonical / max(pages_analyzed, 1)) * 100, 1
                    ),
                    # Schema Markup
                    "schema_pages": pages_with_schema,
                    "schema_coverage": round(
                        (pages_with_schema / max(pages_analyzed, 1)) * 100, 1
                    ),
                    # Robots.txt
                    "robots_status": (
                        "Found" if robots_info.get("exists", False) else "Missing"
                    ),
                    "robots_disallow_rules": len(
                        robots_info.get("disallow_patterns", [])
                    ),
                    "robots_sitemaps": len(robots_info.get("sitemaps", [])),
                    # Sitemap
                    "sitemap_status": (
                        "Found" if sitemap_info.get("exists", False) else "Missing"
                    ),
                    # Duplicate Content
                    "duplicate_titles": content_details.get("duplicate_titles", 0),
                    "duplicate_meta_descriptions": content_details.get(
                        "duplicate_meta_descriptions", 0
                    ),
                    "duplicate_h1_tags": content_details.get("duplicate_h1_tags", 0),
                },
            },
            # Content Analysis (Pages Analysis)
            "pages_analysis": {
                "score": score_breakdown.get("content", 0),
                "issues": content_analysis.get("issues", []),
                "pages": enhanced_results.get(
                    "crawled_pages", {}
                ),  # Add individual pages data
                "details": {
                    # Title Analysis
                    "avg_title_length": round(avg_title_length, 1),
                    "titles_too_short": len([l for l in title_lengths if l < 30]),
                    "titles_too_long": len([l for l in title_lengths if l > 60]),
                    "missing_titles": missing_titles,
                    # Meta Description Analysis
                    "avg_meta_description_length": round(avg_meta_length, 1),
                    "meta_too_short": len([l for l in meta_lengths if l < 120]),
                    "meta_too_long": len([l for l in meta_lengths if l > 160]),
                    "missing_meta_descriptions": missing_meta,
                    # Image Analysis
                    "total_images": total_images,
                    "images_missing_alt": missing_alt,
                    "alt_text_coverage": round(
                        ((total_images - missing_alt) / max(total_images, 1)) * 100, 1
                    ),
                },
            },
            # Performance Analysis (Site-wide Issues)
            "site_wide_issues": {
                "score": score_breakdown.get("performance", 0),
                "issues": performance.get("issues", []),
                "details": {
                    "avg_page_size": round(avg_page_size, 1),
                    "avg_load_time": round(avg_load_time, 2),
                    "performance_score": score_breakdown.get("performance", 0),
                    "largest_contentful_paint": performance_details.get("lcp", 0),
                    "first_input_delay": performance_details.get("fid", 0),
                    "cumulative_layout_shift": performance_details.get("cls", 0),
                },
            },
            # Other required fields
            "recommendations": recommendations,
            "crawl_summary": {
                "total_pages_found": pages_analyzed,
                "successfully_crawled": pages_analyzed,
                "failed_pages": 0,
            },
            "robots_txt": {
                "exists": robots_info.get("exists", False),
                "accessible": robots_info.get("accessible", False),
                "content": robots_info.get("content", ""),
                "disallow_patterns": robots_info.get("disallow_patterns", []),
                "sitemaps": robots_info.get("sitemaps", []),
            },
            "sitemap": {
                "exists": sitemap_info.get("exists", False),
                "accessible": sitemap_info.get("accessible", False),
                "url_count": sitemap_info.get("url_count", 0),
            },
        }

        return transformed

    except Exception as e:
        print(f"Error transforming enhanced results: {e}")
        return enhanced_results  # Return original if transformation fails


from ..utils.enhanced_seo_analyzer import ComprehensiveSEOAnalyzer
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
    """SEO Audit Tool - Main interface with real data"""
    user_has_pro = is_premium_user()

    # Get real usage data from database
    usage_info = {"usage_count": 0, "limit": 3, "period": "month"}
    usage_message = "Free users get 3 SEO audits per month with basic overview"

    # Import models
    from app.models.seo_reports import SEOUsageLimit, SEOReport

    if current_user.is_authenticated:
        if not user_has_pro:
            # Get real usage data for free users
            can_use, usage_msg = SEOUsageLimit.can_use_tool(
                current_user.id, is_premium=False
            )
            usage_record = SEOUsageLimit.get_usage_for_user(current_user.id)

            usage_info = {
                "usage_count": usage_record.usage_count,
                "limit": 3,
                "period": "month",
                "can_use": can_use,
            }
            usage_message = usage_msg
        else:
            usage_info = {
                "usage_count": 0,
                "limit": "unlimited",
                "period": "month",
                "can_use": True,
            }
            usage_message = "Premium Plan - Unlimited SEO Audits"

        # Get recent reports for this user
        recent_reports = (
            SEOReport.query.filter_by(user_id=current_user.id)
            .order_by(SEOReport.created_at.desc())
            .limit(5)
            .all()
        )

        # Get user's statistics
        total_reports = SEOReport.query.filter_by(user_id=current_user.id).count()
        avg_score = (
            db.session.query(db.func.avg(SEOReport.overall_score))
            .filter_by(user_id=current_user.id)
            .scalar()
            or 0
        )

    else:
        recent_reports = []
        total_reports = 0
        avg_score = 0
        usage_message = "Sign up for 3 free audits per month, or upgrade to Premium for unlimited access"

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
        # New real data
        recent_reports=recent_reports,
        total_reports=total_reports,
        avg_score=round(avg_score, 1) if avg_score else 0,
        user_stats={
            "total_audits": total_reports,
            "avg_score": round(avg_score, 1) if avg_score else 0,
            "recent_reports": len(recent_reports),
            "is_premium": user_has_pro,
        },
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

        # Perform comprehensive SEO audit with enhanced analyzer
        try:
            print(f"DEBUG: Creating enhanced analyzer for {url}")
            enhanced_analyzer = ComprehensiveSEOAnalyzer(
                url, is_premium=user_is_premium
            )
            print(f"DEBUG: Running comprehensive audit...")
            enhanced_results = enhanced_analyzer.perform_comprehensive_audit()
            print(
                f"DEBUG: Enhanced analyzer result success: {enhanced_results.get('success', False)}"
            )

            # Transform enhanced results to match expected format
            if enhanced_results.get("success"):
                print(f"DEBUG: Transforming enhanced results...")
                audit_results = transform_enhanced_results(enhanced_results)
                print(f"DEBUG: Transformation completed successfully")
            else:
                print(
                    f"DEBUG: Enhanced analyzer failed, falling back to basic analyzer"
                )
                # Fallback to basic analyzer if enhanced fails
                audit_results = audit_seo(url, is_premium=user_is_premium)
        except Exception as analyzer_error:
            print(f"Enhanced analyzer failed: {analyzer_error}, falling back to basic")
            import traceback

            traceback.print_exc()
            audit_results = audit_seo(url, is_premium=user_is_premium)

        if audit_results.get("success"):
            # Save audit to database for real usage tracking
            try:
                from app.models.seo_reports import SEOReport, SEOUsageLimit
                from urllib.parse import urlparse
                import hashlib

                # Extract domain from URL
                parsed_url = urlparse(
                    url if url.startswith("http") else f"https://{url}"
                )
                domain = parsed_url.netloc or parsed_url.path.split("/")[0]

                # Create report hash for sharing
                report_hash = hashlib.md5(
                    f"{url}_{datetime.now().isoformat()}".encode()
                ).hexdigest()

                # Create SEO report record
                seo_report = SEOReport(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    website_url=url,
                    domain=domain,
                    overall_score=audit_results.get("overall_score", 0),
                    pages_analyzed=audit_results.get("crawl_summary", {}).get(
                        "successfully_crawled", 0
                    ),
                    issues_found=len(audit_results.get("recommendations", [])),
                    audit_duration=audit_results.get("total_audit_time", 0),
                    report_hash=report_hash,
                    is_public=False,
                )

                # Set audit data
                seo_report.audit_data = audit_results

                # Add to database
                db.session.add(seo_report)

                # Update usage limits for free users
                if current_user.is_authenticated and not user_is_premium:
                    SEOUsageLimit.increment_usage(current_user.id)

                db.session.commit()

                # Add report ID to results
                audit_results["report_id"] = seo_report.id
                audit_results["report_hash"] = report_hash

            except Exception as save_error:
                print(f"Error saving audit report: {str(save_error)}")
                # Don't fail the whole request if saving fails
                db.session.rollback()

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

        # Perform comprehensive SEO audit with enhanced analyzer
        try:
            enhanced_analyzer = ComprehensiveSEOAnalyzer(
                url, is_premium=user_is_premium
            )
            enhanced_results = enhanced_analyzer.perform_comprehensive_audit()

            # Transform enhanced results to match expected format
            if enhanced_results.get("success"):
                audit_results = transform_enhanced_results(enhanced_results)
            else:
                # Fallback to basic analyzer if enhanced fails
                audit_results = audit_seo(url, is_premium=user_is_premium)
        except Exception as analyzer_error:
            print(f"Enhanced analyzer failed: {analyzer_error}, falling back to basic")
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
    """SEO Reports History - Show real user reports"""
    from app.models.seo_reports import SEOReport

    # Get user's reports
    reports = (
        SEOReport.query.filter_by(user_id=current_user.id)
        .order_by(SEOReport.created_at.desc())
        .all()
    )

    return render_template(
        "tools/seo_reports_history.html",
        reports=reports,
        user_has_pro=is_premium_user(),
        user_is_authenticated=True,
        total_reports=len(reports),
        avg_score=(
            sum(r.overall_score for r in reports) / len(reports) if reports else 0
        ),
    )


@seo_tools_bp.route("/report/<int:report_id>")
def view_report(report_id):
    """View individual SEO report"""
    from app.models.seo_reports import SEOReport

    report = SEOReport.query.get_or_404(report_id)

    # Check if user can access this report
    if (
        report.user_id
        and current_user.is_authenticated
        and report.user_id != current_user.id
    ):
        if not report.is_public:
            flash("You don't have permission to view this report.", "error")
            return redirect(url_for("seo_tools.seo_audit_tool"))

    # Determine which template to use based on audit data structure
    template_name = "tools/seo_report_detail.html"

    # If we have comprehensive audit data, use the enhanced template
    if (
        report.audit_data
        and isinstance(report.audit_data, dict)
        and (
            "technical_seo" in report.audit_data
            or "content_analysis" in report.audit_data
            or "performance" in report.audit_data
        )
    ):
        template_name = "tools/seo_report_comprehensive.html"

    return render_template(
        template_name,
        report=report,
        audit_data=report.audit_data,
        user_has_pro=is_premium_user() if current_user.is_authenticated else False,
        user_is_authenticated=current_user.is_authenticated,
    )


@seo_tools_bp.route("/report/<report_hash>")
def view_shared_report(report_hash):
    """View shared SEO report by hash"""
    from app.models.seo_reports import SEOReport

    report = SEOReport.query.filter_by(report_hash=report_hash).first_or_404()

    return render_template(
        "tools/seo_report_detail.html",
        report=report,
        audit_data=report.audit_data,
        user_has_pro=is_premium_user() if current_user.is_authenticated else False,
        user_is_authenticated=current_user.is_authenticated,
        is_shared=True,
    )


@seo_tools_bp.route("/report/<int:report_id>/pdf")
@login_required
def download_report_pdf(report_id):
    """Download SEO report as PDF - Premium only"""
    from app.models.seo_reports import SEOReport

    # Check if user is premium
    if not is_premium_user():
        flash("PDF downloads are available for Premium users only.", "warning")
        return redirect(url_for("main.pricing"))

    # Get the report
    report = SEOReport.query.get_or_404(report_id)

    # Check if user owns the report or if it's public
    if not report.is_public and report.user_id != current_user.id:
        flash("You don't have permission to access this report.", "error")
        return redirect(url_for("seo_tools.seo_reports_history"))

    # Generate and return PDF for premium users
    try:
        from app.utils.pdf_generator import generate_seo_report_pdf

        # Generate PDF content
        pdf_content = generate_seo_report_pdf(report)

        # Create response with PDF
        response = make_response(pdf_content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            f'attachment; filename="seo_report_{report_id}.pdf"'
        )

        flash("PDF report generated successfully!", "success")
        return response

    except ImportError:
        # Fallback if PDF generator not available
        flash(
            "PDF generation is temporarily unavailable. Please try again later.",
            "warning",
        )
        return redirect(url_for("seo_tools.view_report", report_id=report_id))
    except Exception as e:
        # Handle any other errors
        flash("Error generating PDF report. Please try again.", "error")
        return redirect(url_for("seo_tools.view_report", report_id=report_id))


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
