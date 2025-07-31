"""
Simplified main tools blueprint - Index and coordination only
Individual tools are now in separate route files for better scalability
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
from flask_login import current_user
import logging

# Create the main tools blueprint (for index and coordination only)
tools_bp = Blueprint("tools", __name__, url_prefix="/tools")
logger = logging.getLogger(__name__)


def register_tool_blueprints(app):
    """Register all tool blueprints using the modular route system."""
    from app.blueprints.tools.routes import register_tool_routes

    # Register all modular tool routes
    registered_count = register_tool_routes(app)

    print(
        f"✅ Modular tool routing system activated - {registered_count} route blueprints registered"
    )
    return registered_count


@tools_bp.route("/")
def tools_index():
    """Main tools page with comprehensive SEO tool collection."""

    # Comprehensive SEO tools data with proper categorization
    tools_data = {
        "Technical SEO": [
            {
                "name": "SEO Audit Tool",
                "slug": "seo/audit-tool",  # Updated to use modular routing
                "description": "Comprehensive SEO analysis with unlimited page crawling, A+ to F scoring, and professional PDF reports",
                "is_premium": True,
                "category": {"name": "Technical SEO"},
            },
            {
                "name": "Site Speed Analyzer",
                "slug": "seo/speed-analyzer",  # Updated to use modular routing
                "description": "Advanced Core Web Vitals analysis with performance optimization recommendations",
                "is_premium": True,
                "category": {"name": "Technical SEO"},
            },
            {
                "name": "Schema Markup Validator",
                "slug": "seo/schema-validator",  # Updated to use modular routing
                "description": "Validate and optimize structured data for better search visibility",
                "is_premium": False,
                "category": {"name": "Technical SEO"},
            },
        ],
        "Content Analysis": [
            {
                "name": "Content Gap Analyzer",
                "slug": "content/gap-analyzer",  # Updated to use modular routing
                "description": "Discover content opportunities by analyzing competitor strategies",
                "is_premium": True,
                "category": {"name": "Content Analysis"},
            },
            {
                "name": "Readability Checker",
                "slug": "content/readability-checker",  # Updated to use modular routing
                "description": "Analyze content readability and optimize for better user engagement",
                "is_premium": False,
                "category": {"name": "Content Analysis"},
            },
            {
                "name": "Meta Tag Generator",
                "slug": "content/meta-tag-generator",  # Updated to use modular routing
                "description": "Generate optimized meta titles and descriptions for better CTR",
                "is_premium": False,
                "category": {"name": "Content Analysis"},
            },
        ],
        "Keyword Research": [
            {
                "name": "Keyword Difficulty Analyzer",
                "slug": "keywords/difficulty-analyzer",  # Updated to use modular routing
                "description": "Analyze keyword competition and discover ranking opportunities",
                "is_premium": True,
                "category": {"name": "Keyword Research"},
            },
            {
                "name": "Long-tail Keyword Finder",
                "slug": "keywords/longtail-finder",  # Updated to use modular routing
                "description": "Find profitable long-tail keywords with lower competition",
                "is_premium": True,
                "category": {"name": "Keyword Research"},
            },
            {
                "name": "Keyword Density Checker",
                "slug": "keywords/density-checker",  # Updated to use modular routing
                "description": "Analyze keyword density and optimize content for target keywords",
                "is_premium": False,
                "category": {"name": "Keyword Research"},
            },
        ],
        "Link Building": [
            {
                "name": "Backlink Quality Analyzer",
                "slug": "links/backlink-analyzer",  # Updated to use modular routing
                "description": "Analyze backlink profiles and identify toxic links for disavowal",
                "is_premium": True,
                "category": {"name": "Link Building"},
            },
            {
                "name": "Broken Link Checker",
                "slug": "links/broken-link-checker",  # Updated to use modular routing
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
        tools_by_category=tools_data,
        tools=all_tools,
        categories=categories,
        total_tools=total_tools,
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )


# Backward compatibility redirects for old URLs
@tools_bp.route("/seo-audit-tool")
def seo_audit_redirect():
    """Redirect old SEO audit URL to new modular route"""
    return redirect(url_for("seo_tools.seo_audit_tool"))


@tools_bp.route("/seo-audit-tool/analyze", methods=["POST"])
def seo_analyze_redirect():
    """Redirect old SEO analyze URL to new modular route"""
    return redirect(
        url_for("seo_tools.analyze_seo"), code=307
    )  # 307 preserves POST method


@tools_bp.route("/seo-reports")
def seo_reports_redirect():
    """Redirect old SEO reports URL to new modular route"""
    return redirect(url_for("seo_tools.seo_reports_history"))


# Generic tool placeholder handler (for tools not yet implemented)
@tools_bp.route("/<path:tool_path>")
def tool_placeholder(tool_path):
    """Handle requests for tools that are in development."""

    # This route catches any undefined tool paths and shows coming soon page
    # The modular routes will take precedence over this catch-all

    return render_template(
        "tools/coming_soon.html",
        tool={
            "name": "Tool Coming Soon",
            "description": "This tool is currently under development",
            "is_premium": False,
            "category": "General",
            "features": ["Coming soon..."],
        },
        user_has_pro=current_user.is_authenticated and current_user.is_pro_user(),
        user_is_authenticated=current_user.is_authenticated,
    )
