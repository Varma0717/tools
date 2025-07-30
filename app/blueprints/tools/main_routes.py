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
        ("broken_link_checker", "broken_link_checker_bp"),
        ("canonical_tag_checker", "canonical_tag_checker_bp"),
        ("content_optimizer", "content_optimizer_bp"),
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
        ("schema_generator", "schema_generator_bp"),
        ("schema_markup_tester", "schema_markup_tester_bp"),
        ("seo_audit_tool", "seo_audit_tool_bp"),
        ("sitemap_xml_validator", "sitemap_xml_validator_bp"),
        ("speed_tester", "speed_tester_bp"),
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
            # Silently skip tools that can't be registered to avoid spam
            pass


@tools_bp.route("/")
def tools_index():
    """Main tools page with static data - comprehensive tool list."""

    # Comprehensive static tools data
    tools_data = {
        "Technical SEO": [
            {
                "name": "SEO Audit Tool",
                "slug": "seo-audit-tool",
                "description": "Comprehensive SEO analysis for your website",
                "is_premium": False,
                "category": {"name": "Technical SEO"},
            },
            {
                "name": "Meta Tag Analyzer",
                "slug": "meta-tag-analyzer",
                "description": "Analyze and optimize your meta tags",
                "is_premium": False,
                "category": {"name": "Technical SEO"},
            },
            {
                "name": "Canonical Tag Checker",
                "slug": "canonical-tag-checker",
                "description": "Check canonical tag implementation",
                "is_premium": False,
            },
            {
                "name": "Schema Markup Tester",
                "slug": "schema-markup-tester",
                "description": "Test and validate schema markup",
                "is_premium": False,
            },
            {
                "name": "Robots.txt Tester",
                "slug": "robots-txt-tester",
                "description": "Test and validate robots.txt file",
                "is_premium": False,
            },
            {
                "name": "SSL Checker",
                "slug": "ssl-checker",
                "description": "Verify SSL certificate status",
                "is_premium": False,
            },
            {
                "name": "HTTP Header Checker",
                "slug": "http-header-checker",
                "description": "Analyze HTTP response headers",
                "is_premium": False,
            },
            {
                "name": "Hreflang Tag Checker",
                "slug": "hreflang-tag-checker",
                "description": "Check hreflang tag implementation",
                "is_premium": False,
            },
        ],
        "Performance": [
            {
                "name": "Page Speed Analyzer",
                "slug": "page-speed-analyzer",
                "description": "Test your website loading speed",
                "is_premium": False,
            },
            {
                "name": "Mobile Optimization Tester",
                "slug": "mobile-optimization-tester",
                "description": "Test mobile optimization",
                "is_premium": False,
            },
            {
                "name": "Image Compressor",
                "slug": "image-compressor",
                "description": "Compress images for better performance",
                "is_premium": False,
            },
            {
                "name": "JavaScript Minifier",
                "slug": "javascript-minifier",
                "description": "Minify JavaScript code",
                "is_premium": False,
            },
        ],
        "Content Analysis": [
            {
                "name": "Content Optimizer",
                "slug": "content-optimizer",
                "description": "Optimize your content for SEO",
                "is_premium": False,
            },
            {
                "name": "Keyword Density Analyzer",
                "slug": "keyword-density-analyzer",
                "description": "Analyze keyword density in your content",
                "is_premium": False,
            },
            {
                "name": "Headline Generator",
                "slug": "headline-generator",
                "description": "Generate compelling headlines",
                "is_premium": False,
            },
        ],
        "Keyword Research": [
            {
                "name": "Advanced Keyword Research",
                "slug": "advanced-keyword-research",
                "description": "Advanced keyword research tool",
                "is_premium": True,
            },
            {
                "name": "Keyword Suggestion Generator",
                "slug": "keyword-suggestion-generator",
                "description": "Generate keyword suggestions",
                "is_premium": False,
            },
            {
                "name": "LSI Keyword Generator",
                "slug": "lsi-keyword-generator",
                "description": "Generate LSI keywords",
                "is_premium": False,
            },
        ],
        "Link Analysis": [
            {
                "name": "Advanced Backlink Analyzer",
                "slug": "advanced-backlink-analyzer",
                "description": "Advanced backlink analysis",
                "is_premium": True,
            },
            {
                "name": "Internal Link Analyzer",
                "slug": "internal-link-analyzer",
                "description": "Analyze internal link structure",
                "is_premium": False,
            },
            {
                "name": "Link Status Monitor",
                "slug": "link-status-monitor",
                "description": "Monitor link status and health",
                "is_premium": False,
            },
            {
                "name": "Broken Link Checker",
                "slug": "broken-link-checker",
                "description": "Find and fix broken links",
                "is_premium": False,
            },
        ],
        "Social Media": [
            {
                "name": "Open Graph Preview",
                "slug": "open-graph-preview",
                "description": "Preview how your page looks on social media",
                "is_premium": False,
            },
        ],
        "Domain Analysis": [
            {
                "name": "DNS Lookup",
                "slug": "dns-lookup",
                "description": "Perform DNS record lookup",
                "is_premium": False,
            },
            {
                "name": "WHOIS Lookup",
                "slug": "whois-lookup",
                "description": "Domain WHOIS information lookup",
                "is_premium": False,
            },
            {
                "name": "Redirect Checker",
                "slug": "redirect-checker",
                "description": "Check redirect chains and status",
                "is_premium": False,
            },
        ],
        "Other": [
            {
                "name": "Speed Tester",
                "slug": "speed-tester",
                "description": "Comprehensive website speed test",
                "is_premium": False,
            },
            {
                "name": "Schema Generator",
                "slug": "schema-generator",
                "description": "Generate structured data",
                "is_premium": False,
            },
            {
                "name": "Sitemap XML Validator",
                "slug": "sitemap-xml-validator",
                "description": "Validate XML sitemap structure",
                "is_premium": False,
            },
            {
                "name": "Password Generator",
                "slug": "password-generator",
                "description": "Generate secure passwords",
                "is_premium": False,
            },
        ],
    }

    # Calculate total tools count and categorize
    total_tools = sum(len(tools) for tools in tools_data.values())
    categories = [
        {"name": cat, "slug": cat.lower().replace(" ", "-")}
        for cat in tools_data.keys()
    ]

    return render_template(
        "tools/index.html",
        tools_data=tools_data,
        categories=categories,
        total_tools=total_tools,
    )


# No generic tool routes - all tools have their own specific routes
# This prevents "Coming Soon" pages from appearing
