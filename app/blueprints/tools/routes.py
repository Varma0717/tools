"""
Simplified tools blueprint that registers working tools only.
"""

from flask import Blueprint, render_template

# Create the main tools blueprint
tools_bp = Blueprint("tools", __name__, url_prefix="/tools")


def register_tool_blueprints(app):
    """Register individual tool blueprints with graceful error handling."""

    tools_registered = 0

    # List of all available tool modules
    tool_modules = [
        ("advanced_keyword_research", "advanced_keyword_research_bp"),
        ("advanced_backlink_analyzer", "advanced_backlink_analyzer_bp"),
        ("technical_seo_analyzer", "technical_seo_analyzer_bp"),
        ("content_optimizer", "content_optimizer_bp"),
        ("schema_generator", "schema_generator_bp"),
        ("speed_tester", "speed_tester_bp"),
        ("broken_link_checker", "broken_link_checker_bp"),
        ("canonical_tag_checker", "canonical_tag_checker_bp"),
        ("dns_lookup", "dns_lookup_bp"),
        ("headline_generator", "headline_generator_bp"),
        ("hreflang_tag_checker", "hreflang_tag_checker_bp"),
        ("http_header_checker", "http_header_checker_bp"),
        ("image_compressor", "image_compressor_bp"),
        ("internal_link_analyzer", "internal_link_analyzer_bp"),
        ("javascript_minifier", "javascript_minifier_bp"),
        ("keyword_density_analyzer", "keyword_density_analyzer_bp"),
        ("keyword_suggestion_generator", "keyword_suggestion_generator_bp"),
        ("link_status_monitor", "link_status_monitor_bp"),
        ("lsi_keyword_generator", "lsi_keyword_generator_bp"),
        ("meta_tag_analyzer", "meta_tag_analyzer_bp"),
        ("mobile_optimization_tester", "mobile_optimization_tester_bp"),
        ("open_graph_preview", "open_graph_preview_bp"),
        ("page_speed_analyzer", "page_speed_analyzer_bp"),
        ("password_generator", "password_generator_bp"),
        ("redirect_checker", "redirect_checker_bp"),
        ("robots_txt_tester", "robots_txt_tester_bp"),
        ("schema_markup_tester", "schema_markup_tester_bp"),
        ("seo_audit_tool", "seo_audit_tool_bp"),
        ("sitemap_xml_validator", "sitemap_xml_validator_bp"),
        ("ssl_checker", "ssl_checker_bp"),
        ("whois_lookup", "whois_lookup_bp"),
    ]

    # Register each tool blueprint
    for module_name, blueprint_name in tool_modules:
        try:
            module = __import__(
                f"app.blueprints.tools.routes.{module_name}", fromlist=[blueprint_name]
            )
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint)
            tools_registered += 1
        except Exception as e:
            pass  # Silently skip tools that can't be registered


@tools_bp.route("/")
def tools_index():
    """Main tools page with static data."""
    # Static tools data to replace database dependency
    tools = [
        {
            "name": "SEO Audit Tool",
            "slug": "seo-audit-tool",
            "description": "Comprehensive SEO analysis for your website",
            "category": {"name": "Analysis"},
            "is_premium": False,
            "requires_login": False,
            "icon": "search",
        },
        {
            "name": "Meta Tag Analyzer",
            "slug": "meta-tag-analyzer",
            "description": "Analyze and optimize your meta tags",
            "category": {"name": "On-Page SEO"},
            "is_premium": False,
            "requires_login": False,
            "icon": "tag",
        },
        {
            "name": "Page Speed Analyzer",
            "slug": "page-speed-analyzer",
            "description": "Test your website's loading speed",
            "category": {"name": "Performance"},
            "is_premium": False,
            "requires_login": False,
            "icon": "zap",
        },
        {
            "name": "Keyword Density Analyzer",
            "slug": "keyword-density-analyzer",
            "description": "Analyze keyword density in your content",
            "category": {"name": "Content"},
            "is_premium": False,
            "requires_login": False,
            "icon": "type",
        },
    ]

    categories = [
        {"name": "Analysis", "slug": "analysis"},
        {"name": "On-Page SEO", "slug": "on-page-seo"},
        {"name": "Performance", "slug": "performance"},
        {"name": "Content", "slug": "content"},
    ]

    return render_template("tools/index.html", tools=tools, categories=categories)


@tools_bp.route("/<slug>")
def tool_detail(slug):
    """Redirect to the actual tool functionality."""
    from flask import abort, redirect

    # Map tool slugs to their actual URLs (since tools use different URL patterns)
    tool_urls = {
        # Core Tools
        "seo-audit-tool": "/tools/seo-audit/",
        "meta-tag-analyzer": "/tools/meta-tag-analyzer/",
        "page-speed-analyzer": "/tools/page-speed-analyzer/",
        "keyword-density-analyzer": "/tools/keyword-density-analyzer/",
        # Advanced Tools
        "advanced-keyword-research": "/tools/advanced-keyword-research/",
        "advanced-backlink-analyzer": "/tools/advanced-backlink-analyzer/",
        "technical-seo-analyzer": "/tools/technical-seo-analyzer",
        "content-optimizer": "/content-optimizer/",
        "schema-generator": "/tools/schema-generator/",
        "speed-tester": "/tools/speed-tester/",
        # Existing Tools
        "seo-audit-tool": "/tools/seo-audit/",
        "meta-tag-analyzer": "/tools/meta-tag-analyzer",
        "canonical-tag-checker": "/tools/canonical-tag-checker",
        "open-graph-preview": "/tools/open-graph-preview",
        "schema-markup-tester": "/tools/schema-markup-tester",
        "sitemap-xml-validator": "/tools/sitemap-xml-validator",
        "robots-txt-tester": "/tools/robots-txt-tester",
        "ssl-checker": "/tools/ssl-checker",
        "http-header-checker": "/tools/http-header-checker",
        "mobile-optimization-tester": "/tools/mobile-optimization/",
        "hreflang-tag-checker": "/tools/hreflang-tag-checker",
        "keyword-density-analyzer": "/tools/keyword-density-analyzer",
        "headline-analyzer": "/tools/headline-generator",
        "broken-link-checker": "/tools/broken-link-checker",
        "link-status-monitor": "/tools/link-status-monitor",
        "internal-link-analyzer": "/tools/internal-link-analyzer",
        "redirect-checker": "/tools/redirect-checker",
        "page-speed-analyzer": "/tools/page-speed-analyzer",
        "image-compressor": "/tools/image-compressor",
        "javascript-minifier": "/tools/javascript-minifier",
        "keyword-suggestion-generator": "/tools/keyword-suggestion-generator",
        "lsi-keyword-generator": "/tools/lsi-keyword-generator",
        "dns-lookup": "/tools/dns-lookup",
        "whois-lookup": "/tools/whois-lookup",
        "password-generator": "/tools/password-generator",
    }

    # Get the URL for this tool
    tool_url = tool_urls.get(slug)
    if tool_url:
        return redirect(tool_url)
    else:
        return f"Tool '{slug}' endpoint not configured yet.", 404


# Remove database-dependent category route
# @tools_bp.route("/category/<int:category_id>")
# def category_tools(category_id):
