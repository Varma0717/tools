"""
Simplified tools blueprint - SEO Audit Tool ONLY
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
    abort,
)
from flask_wtf.csrf import generate_csrf
from flask_login import current_user, login_required
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf, db
from app.blueprints.tools.utils.seo_audit_tool_utils import audit_seo
from app.models.seo_reports import SEOReport, SEOUsageLimit
from urllib.parse import urlparse
import logging
import re
import hashlib
import time

# Create the main tools blueprint
tools_bp = Blueprint("tools", __name__, url_prefix="/tools")
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
    return url_pattern.match(url) is not None


@tools_bp.route("/seo-audit-tool")
@login_required
def tools_seo_audit_tool():
    """Display the SEO audit tool page."""
    # Check usage limits for non-premium users
    can_use, message = SEOUsageLimit.can_use_tool(
        current_user.id, current_user.is_premium
    )

    if not can_use:
        flash(message, "warning")
        return redirect(url_for("main.pricing"))

    csrf_token = generate_csrf()
    usage_info = SEOUsageLimit.get_usage_for_user(current_user.id)

    return render_template(
        "tools/seo_audit_tool.html",
        csrf_token=csrf_token,
        usage_info=usage_info,
        can_use=can_use,
        usage_message=message,
        is_premium=current_user.is_premium,
    )


@tools_bp.route("/seo-audit-tool/analyze", methods=["POST"])
@csrf.exempt
@login_required
def tools_analyze_seo():
    """Analyze website SEO and return results."""
    try:
        # Check usage limits first
        can_use, message = SEOUsageLimit.can_use_tool(
            current_user.id, current_user.is_premium
        )

        if not can_use:
            return jsonify({"error": message}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Validate URL
        if not is_valid_url(url):
            return jsonify({"error": "Please enter a valid URL"}), 400

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        logger.info(f"Analyzing URL: {url} for user: {current_user.id}")

        # Increment usage count for non-premium users
        if not current_user.is_premium:
            SEOUsageLimit.increment_usage(current_user.id)

        # Perform SEO audit with premium features for Pro users
        start_time = time.time()
        is_premium_user = current_user.is_pro_user()
        result = audit_seo(url, is_premium=is_premium_user)
        audit_duration = time.time() - start_time

        if result.get("error"):
            logger.error(f"SEO audit failed for {url}: {result['error']}")
            return jsonify({"error": result["error"]}), 400

        # Save report to database
        domain = urlparse(url).netloc
        report_hash = hashlib.md5(
            f"{url}_{current_user.id}_{time.time()}".encode()
        ).hexdigest()

        # Count issues
        issues_count = len(result.get("recommendations", []))

        seo_report = SEOReport(
            user_id=current_user.id,
            website_url=url,
            domain=domain,
            overall_score=result.get("overall_score", 0),
            pages_analyzed=result.get("crawl_summary", {}).get(
                "successfully_crawled", 0
            ),
            issues_found=issues_count,
            audit_duration=audit_duration,
            report_hash=report_hash,
        )
        seo_report.audit_data = result

        db.session.add(seo_report)
        db.session.commit()

        # Add report ID to response
        result["report_id"] = seo_report.id
        result["report_hash"] = report_hash

        # For free users, limit the results
        if not current_user.is_premium:
            limited_result = {
                "overall_score": result.get("overall_score", 0),
                "crawl_summary": result.get("crawl_summary", {}),
                "report_id": seo_report.id,
                "report_hash": report_hash,
                "limited_access": True,
                "upgrade_required": True,
                "recommendations": result.get("recommendations", [])[
                    :3
                ],  # Only first 3 recommendations
                "message": "This is a limited preview. Upgrade to Pro for complete analysis including technical SEO, content insights, and performance metrics.",
            }
            result = limited_result

        logger.info(
            f"SEO audit completed successfully for {url}, saved as report ID: {seo_report.id}"
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error during SEO analysis: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


def register_tool_blueprints(app):
    """Register tool blueprints - now simplified since everything is in main tools_bp."""
    # No separate blueprints to register - everything is in tools_bp now
    print("✅ All tools integrated into main tools blueprint")
    return 1


@tools_bp.route("/seo-reports")
@login_required
def seo_reports_history():
    """Display SEO reports history for user"""
    page = request.args.get("page", 1, type=int)
    per_page = 10

    reports = (
        SEOReport.query.filter_by(user_id=current_user.id)
        .order_by(SEOReport.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "tools/seo_reports_history.html",
        reports=reports,
        current_user=current_user,
        user_is_pro=current_user.is_pro_user(),
    )


@tools_bp.route("/seo-report/<int:report_id>")
@login_required
def view_seo_report(report_id):
    """View detailed SEO report"""
    report = SEOReport.query.filter_by(
        id=report_id, user_id=current_user.id
    ).first_or_404()

    user_is_pro = current_user.is_pro_user()
    audit_data = report.audit_data

    # For free users, limit data access and show upgrade prompts
    if not user_is_pro:
        # Provide limited audit data for free users
        limited_audit_data = {
            "overall_score": audit_data.get("overall_score", 0),
            "crawl_summary": audit_data.get("crawl_summary", {}),
            "limited_access": True,
            "upgrade_required": True,
        }
        audit_data = limited_audit_data

    return render_template(
        "tools/seo_report_detail.html",
        report=report,
        audit_data=audit_data,
        user_is_pro=user_is_pro,
    )


@tools_bp.route("/seo-report/<int:report_id>/pdf")
@login_required
def download_seo_report_pdf(report_id):
    """Download SEO report as PDF"""
    report = SEOReport.query.filter_by(
        id=report_id, user_id=current_user.id
    ).first_or_404()

    # Check if user is Pro for PDF downloads
    if not current_user.is_pro_user():
        flash(
            "PDF downloads are available for Pro users only. Upgrade to unlock this feature.",
            "warning",
        )
        return redirect(url_for("main.pricing"))

    try:
        from app.utils.pdf_generator import generate_seo_report_pdf

        pdf_data = generate_seo_report_pdf(report)

        response = make_response(pdf_data)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            f'attachment; filename=seo_report_{report.domain}_{report.created_at.strftime("%Y%m%d")}.pdf'
        )

        return response
    except ImportError:
        flash("PDF generation is not available. Please contact support.", "error")
        return redirect(url_for("tools.view_seo_report", report_id=report_id))


@tools_bp.route("/seo-report/<report_hash>/public")
def view_public_seo_report(report_hash):
    """View public SEO report (shareable link)"""
    report = SEOReport.query.filter_by(
        report_hash=report_hash, is_public=True
    ).first_or_404()

    return render_template(
        "tools/seo_report_public.html", report=report, audit_data=report.audit_data
    )


@tools_bp.route("/")
def tools_index():
    """Main tools page with comprehensive SEO tool collection."""

    # Comprehensive SEO tools data with proper categorization
    tools_data = {
        "Technical SEO": [
            {
                "name": "SEO Audit Tool",
                "slug": "seo-audit-tool",
                "description": "Comprehensive SEO analysis with unlimited page crawling, A+ to F scoring, and professional PDF reports",
                "is_premium": True,  # Fixed: This is a premium tool with usage limits
                "category": {"name": "Technical SEO"},
            },
            {
                "name": "Site Speed Analyzer",
                "slug": "site-speed-analyzer",
                "description": "Advanced Core Web Vitals analysis with performance optimization recommendations",
                "is_premium": True,
                "category": {"name": "Technical SEO"},
            },
            {
                "name": "Schema Markup Validator",
                "slug": "schema-validator",
                "description": "Validate and optimize structured data for better search visibility",
                "is_premium": False,
                "category": {"name": "Technical SEO"},
            },
        ],
        "Content Analysis": [
            {
                "name": "Content Gap Analyzer",
                "slug": "content-gap-analyzer",
                "description": "Discover content opportunities by analyzing competitor strategies",
                "is_premium": True,
                "category": {"name": "Content Analysis"},
            },
            {
                "name": "Readability Checker",
                "slug": "readability-checker",
                "description": "Analyze content readability and optimize for better user engagement",
                "is_premium": False,
                "category": {"name": "Content Analysis"},
            },
            {
                "name": "Meta Tag Generator",
                "slug": "meta-tag-generator",
                "description": "Generate optimized meta titles and descriptions for better CTR",
                "is_premium": False,
                "category": {"name": "Content Analysis"},
            },
        ],
        "Keyword Research": [
            {
                "name": "Keyword Difficulty Analyzer",
                "slug": "keyword-difficulty",
                "description": "Analyze keyword competition and discover ranking opportunities",
                "is_premium": True,
                "category": {"name": "Keyword Research"},
            },
            {
                "name": "Long-tail Keyword Finder",
                "slug": "longtail-keywords",
                "description": "Find profitable long-tail keywords with lower competition",
                "is_premium": True,
                "category": {"name": "Keyword Research"},
            },
            {
                "name": "Keyword Density Checker",
                "slug": "keyword-density",
                "description": "Analyze keyword density and optimize content for target keywords",
                "is_premium": False,
                "category": {"name": "Keyword Research"},
            },
        ],
        "Link Building": [
            {
                "name": "Backlink Quality Analyzer",
                "slug": "backlink-analyzer",
                "description": "Analyze backlink profiles and identify toxic links for disavowal",
                "is_premium": True,
                "category": {"name": "Link Building"},
            },
            {
                "name": "Broken Link Checker",
                "slug": "broken-link-checker",
                "description": "Find and fix broken links that hurt your SEO performance",
                "is_premium": False,
                "category": {"name": "Link Building"},
            },
        ],
    }

    # Calculate total tools count and categorize
    total_tools = sum(len(tools) for tools in tools_data.values())
    categories = [
        {"name": cat, "slug": cat.lower().replace(" ", "-")}
        for cat in tools_data.keys()
    ]

    # Flatten tools for template compatibility
    all_tools = []
    for category_tools in tools_data.values():
        all_tools.extend(category_tools)

    # Check if user has premium access
    user_has_pro = False
    if current_user.is_authenticated:
        user_has_pro = current_user.is_pro_user()

    return render_template(
        "tools/index.html",
        tools_data=tools_data,
        tools_by_category=tools_data,  # Also pass as expected name
        tools=all_tools,  # Add flattened tools list
        categories=categories,
        total_tools=total_tools,
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )


# Placeholder routes for tools in development
@tools_bp.route("/<tool_slug>")
def tool_placeholder(tool_slug):
    """Handle requests for tools that are in development."""

    # Only SEO Audit Tool is fully implemented
    if tool_slug == "seo-audit-tool":
        return redirect(url_for("tools.seo_audit_tool"))

    # For all other tools, show coming soon page
    tool_info = get_tool_info(tool_slug)
    if not tool_info:
        abort(404)

    return render_template(
        "tools/coming_soon.html",
        tool=tool_info,
        user_has_pro=current_user.is_authenticated and current_user.is_pro_user(),
        user_is_authenticated=current_user.is_authenticated,
    )


def get_tool_info(slug):
    """Get tool information by slug."""
    tools_data = {
        "site-speed-analyzer": {
            "name": "Site Speed Analyzer",
            "description": "Advanced Core Web Vitals analysis with performance optimization recommendations",
            "is_premium": True,
            "category": "Technical SEO",
            "features": [
                "Core Web Vitals analysis",
                "Performance bottleneck detection",
                "Optimization recommendations",
                "Mobile speed testing",
                "Competitive performance comparison",
            ],
        },
        "schema-validator": {
            "name": "Schema Markup Validator",
            "description": "Validate and optimize structured data for better search visibility",
            "is_premium": False,
            "category": "Technical SEO",
            "features": [
                "JSON-LD validation",
                "Microdata checking",
                "Rich snippet preview",
                "Schema error detection",
                "Markup recommendations",
            ],
        },
        "content-gap-analyzer": {
            "name": "Content Gap Analyzer",
            "description": "Discover content opportunities by analyzing competitor strategies",
            "is_premium": True,
            "category": "Content Analysis",
            "features": [
                "Competitor content analysis",
                "Gap identification",
                "Topic opportunities",
                "Content planning",
                "Market research insights",
            ],
        },
        "readability-checker": {
            "name": "Readability Checker",
            "description": "Analyze content readability and optimize for better user engagement",
            "is_premium": False,
            "category": "Content Analysis",
            "features": [
                "Flesch-Kincaid scoring",
                "Grade level analysis",
                "Sentence complexity check",
                "Vocabulary assessment",
                "Improvement suggestions",
            ],
        },
        "meta-tag-generator": {
            "name": "Meta Tag Generator",
            "description": "Generate optimized meta titles and descriptions for better CTR",
            "is_premium": False,
            "category": "Content Analysis",
            "features": [
                "Title tag optimization",
                "Meta description generation",
                "Character limit checking",
                "CTR improvement tips",
                "SERP preview",
            ],
        },
        "keyword-difficulty": {
            "name": "Keyword Difficulty Analyzer",
            "description": "Analyze keyword competition and discover ranking opportunities",
            "is_premium": True,
            "category": "Keyword Research",
            "features": [
                "Competition analysis",
                "Difficulty scoring",
                "SERP analysis",
                "Ranking opportunity identification",
                "Traffic potential estimation",
            ],
        },
        "longtail-keywords": {
            "name": "Long-tail Keyword Finder",
            "description": "Find profitable long-tail keywords with lower competition",
            "is_premium": True,
            "category": "Keyword Research",
            "features": [
                "Long-tail keyword discovery",
                "Search volume analysis",
                "Competition assessment",
                "Related keyword suggestions",
                "Intent classification",
            ],
        },
        "keyword-density": {
            "name": "Keyword Density Checker",
            "description": "Analyze keyword density and optimize content for target keywords",
            "is_premium": False,
            "category": "Keyword Research",
            "features": [
                "Keyword density analysis",
                "Over-optimization detection",
                "Related keyword suggestions",
                "Content optimization tips",
                "Competitor comparison",
            ],
        },
        "backlink-analyzer": {
            "name": "Backlink Quality Analyzer",
            "description": "Analyze backlink profiles and identify toxic links for disavowal",
            "is_premium": True,
            "category": "Link Building",
            "features": [
                "Backlink profile analysis",
                "Toxic link detection",
                "Link quality scoring",
                "Disavow file generation",
                "Competitor backlink analysis",
            ],
        },
        "broken-link-checker": {
            "name": "Broken Link Checker",
            "description": "Find and fix broken links that hurt your SEO performance",
            "is_premium": False,
            "category": "Link Building",
            "features": [
                "Internal link checking",
                "External link validation",
                "404 error detection",
                "Redirect chain analysis",
                "Link repair suggestions",
            ],
        },
    }

    return tools_data.get(slug)


# No other tool routes - only SEO Audit Tool exists
