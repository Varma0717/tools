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
                "name": "Keyword Density Analyzer",
                "slug": "keyword-density-analyzer",
                "description": "Analyze keyword density in your content",
                "is_premium": False,
            },
            {
                "name": "Headline Generator",
                "slug": "headline-generator",
                "description": "Generate engaging headlines",
                "is_premium": False,
            },
            {
                "name": "Content Optimizer",
                "slug": "content-optimizer",
                "description": "Optimize content for SEO",
                "is_premium": True,
            },
        ],
        "Keyword Research": [
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
            {
                "name": "Advanced Keyword Research",
                "slug": "advanced-keyword-research",
                "description": "Advanced keyword research tool",
                "is_premium": True,
            },
        ],
        "Link Analysis": [
            {
                "name": "Broken Link Checker",
                "slug": "broken-link-checker",
                "description": "Find and fix broken links",
                "is_premium": False,
            },
            {
                "name": "Link Status Monitor",
                "slug": "link-status-monitor",
                "description": "Monitor link status",
                "is_premium": False,
            },
            {
                "name": "Internal Link Analyzer",
                "slug": "internal-link-analyzer",
                "description": "Analyze internal linking structure",
                "is_premium": False,
            },
            {
                "name": "Redirect Checker",
                "slug": "redirect-checker",
                "description": "Check redirect chains",
                "is_premium": False,
            },
            {
                "name": "Advanced Backlink Analyzer",
                "slug": "advanced-backlink-analyzer",
                "description": "Advanced backlink analysis",
                "is_premium": True,
            },
        ],
        "Technical Tools": [
            {
                "name": "DNS Lookup",
                "slug": "dns-lookup",
                "description": "Perform DNS lookup queries",
                "is_premium": False,
            },
            {
                "name": "WHOIS Lookup",
                "slug": "whois-lookup",
                "description": "Get domain WHOIS information",
                "is_premium": False,
            },
            {
                "name": "Password Generator",
                "slug": "password-generator",
                "description": "Generate secure passwords",
                "is_premium": False,
            },
            {
                "name": "Schema Generator",
                "slug": "schema-generator",
                "description": "Generate schema markup",
                "is_premium": False,
            },
            {
                "name": "Sitemap XML Validator",
                "slug": "sitemap-xml-validator",
                "description": "Validate XML sitemaps",
                "is_premium": False,
            },
        ],
        "Social & Preview": [
            {
                "name": "Open Graph Preview",
                "slug": "open-graph-preview",
                "description": "Preview Open Graph tags",
                "is_premium": False,
            },
        ],
    }

    categories = [
        {"name": "Technical SEO", "slug": "technical-seo", "icon": "search"},
        {"name": "Performance", "slug": "performance", "icon": "zap"},
        {"name": "Content Analysis", "slug": "content-analysis", "icon": "file-text"},
        {"name": "Keyword Research", "slug": "keyword-research", "icon": "target"},
        {"name": "Link Analysis", "slug": "link-analysis", "icon": "link"},
        {"name": "Technical Tools", "slug": "technical-tools", "icon": "tool"},
        {"name": "Social & Preview", "slug": "social-preview", "icon": "share"},
    ]

    # Map tools data to use slugs as keys for template compatibility
    tools_by_category = {
        "technical-seo": tools_data["Technical SEO"],
        "performance": tools_data["Performance"],
        "content-analysis": tools_data["Content Analysis"],
        "keyword-research": tools_data["Keyword Research"],
        "link-analysis": tools_data["Link Analysis"],
        "technical-tools": tools_data["Technical Tools"],
        "social-preview": tools_data["Social & Preview"],
    }

    # Calculate totals for template
    total_tools = sum(len(tools) for tools in tools_data.values())
    tool_counts = {category: len(tools) for category, tools in tools_data.items()}
    tool_counts["total"] = total_tools

    return render_template(
        "tools/index.html",
        tools=tools_data,
        tools_by_category=tools_by_category,  # Template expects this with slug keys
        categories=categories,
        total_tools=total_tools,
        tool_counts=tool_counts,
        page_title="SEO Tools - Complete Toolkit",
        meta_description="Access our comprehensive SEO toolkit with 25+ free and premium tools for technical SEO, content optimization, and website analysis.",
    )

    # Generic tool routes removed to prevent "Coming Soon" pages
    # All tools should have their own specific routes

    # Tool information for creating tool detail pages
    tools_info = {
        # Core Tools
        "meta-tag-analyzer": {
            "name": "Meta Tag Analyzer",
            "description": "Analyze and optimize your meta tags",
            "category": "Technical SEO",
        },
        "page-speed-analyzer": {
            "name": "Page Speed Analyzer",
            "description": "Test your website loading speed",
            "category": "Performance",
        },
        "keyword-density-analyzer": {
            "name": "Keyword Density Analyzer",
            "description": "Analyze keyword density in your content",
            "category": "Content Analysis",
        },
        # Advanced Tools
        "advanced-keyword-research": {
            "name": "Advanced Keyword Research",
            "description": "Advanced keyword research tool",
            "category": "Keyword Research",
        },
        "advanced-backlink-analyzer": {
            "name": "Advanced Backlink Analyzer",
            "description": "Advanced backlink analysis",
            "category": "Link Analysis",
        },
        "technical-seo-analyzer": {
            "name": "Technical SEO Analyzer",
            "description": "Comprehensive technical SEO analysis",
            "category": "Technical SEO",
        },
        "content-optimizer": {
            "name": "Content Optimizer",
            "description": "Optimize content for SEO",
            "category": "Content Analysis",
        },
        "schema-generator": {
            "name": "Schema Generator",
            "description": "Generate schema markup",
            "category": "Technical SEO",
        },
        # Technical SEO Tools
        "canonical-tag-checker": {
            "name": "Canonical Tag Checker",
            "description": "Check canonical tag implementation",
            "category": "Technical SEO",
        },
        "open-graph-preview": {
            "name": "Open Graph Preview",
            "description": "Preview Open Graph tags",
            "category": "Social & Preview",
        },
        "schema-markup-tester": {
            "name": "Schema Markup Tester",
            "description": "Test and validate schema markup",
            "category": "Technical SEO",
        },
        "sitemap-xml-validator": {
            "name": "Sitemap XML Validator",
            "description": "Validate XML sitemaps",
            "category": "Technical SEO",
        },
        "robots-txt-tester": {
            "name": "Robots.txt Tester",
            "description": "Test and validate robots.txt file",
            "category": "Technical SEO",
        },
        "ssl-checker": {
            "name": "SSL Checker",
            "description": "Verify SSL certificate status",
            "category": "Technical SEO",
        },
        "http-header-checker": {
            "name": "HTTP Header Checker",
            "description": "Analyze HTTP response headers",
            "category": "Technical SEO",
        },
        "mobile-optimization-tester": {
            "name": "Mobile Optimization Tester",
            "description": "Test mobile optimization",
            "category": "Performance",
        },
        "hreflang-tag-checker": {
            "name": "Hreflang Tag Checker",
            "description": "Check hreflang tag implementation",
            "category": "Technical SEO",
        },
        # Content Tools
        "headline-generator": {
            "name": "Headline Generator",
            "description": "Generate engaging headlines",
            "category": "Content Analysis",
        },
        # Link Analysis Tools
        "broken-link-checker": {
            "name": "Broken Link Checker",
            "description": "Find and fix broken links",
            "category": "Link Analysis",
        },
        "link-status-monitor": {
            "name": "Link Status Monitor",
            "description": "Monitor link status",
            "category": "Link Analysis",
        },
        "internal-link-analyzer": {
            "name": "Internal Link Analyzer",
            "description": "Analyze internal linking structure",
            "category": "Link Analysis",
        },
        "redirect-checker": {
            "name": "Redirect Checker",
            "description": "Check redirect chains",
            "category": "Link Analysis",
        },
        # Performance Tools
        "image-compressor": {
            "name": "Image Compressor",
            "description": "Compress images for better performance",
            "category": "Performance",
        },
        "javascript-minifier": {
            "name": "JavaScript Minifier",
            "description": "Minify JavaScript code",
            "category": "Performance",
        },
        "core-web-vitals": {
            "name": "Core Web Vitals",
            "description": "Measure Core Web Vitals",
            "category": "Performance",
        },
        # Keyword Research Tools
        "keyword-suggestion-generator": {
            "name": "Keyword Suggestion Generator",
            "description": "Generate keyword suggestions",
            "category": "Keyword Research",
        },
        "lsi-keyword-generator": {
            "name": "LSI Keyword Generator",
            "description": "Generate LSI keywords",
            "category": "Keyword Research",
        },
        # Technical Tools
        "dns-lookup": {
            "name": "DNS Lookup",
            "description": "Perform DNS lookup queries",
            "category": "Technical Tools",
        },
        "whois-lookup": {
            "name": "WHOIS Lookup",
            "description": "Get domain WHOIS information",
            "category": "Technical Tools",
        },
        "password-generator": {
            "name": "Password Generator",
            "description": "Generate secure passwords",
            "category": "Technical Tools",
        },
        # Social & Preview Tools
        "twitter-card-preview": {
            "name": "Twitter Card Preview",
            "description": "Preview Twitter cards",
            "category": "Social & Preview",
        },
        "social-media-preview": {
            "name": "Social Media Preview",
            "description": "Preview social media posts",
            "category": "Social & Preview",
        },
    }

    # Check if we have info for this tool
    if slug in tools_info:
        tool_info = tools_info[slug]

        # Create a tool object for the template
        tool = {
            "name": tool_info["name"],
            "slug": slug,
            "description": tool_info["description"],
            "category": {"name": tool_info["category"]},
            "is_premium": False,  # You can adjust this per tool
        }

        # Render the tool detail template (coming soon page)
        return render_template("tools/tool_detail.html", tool=tool)
    else:
        # Tool not found
        abort(404)


# Category routes disabled - using static tools only
# All tools are available from main tools page
