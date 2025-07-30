"""
Simplified tools blueprint that registers working tools only.
"""

from flask import Blueprint, render_template, redirect, abort

# Create the main tools blueprint
tools_bp = Blueprint("tools", __name__, url_prefix="/tools")


def register_tool_blueprints(app):
    """Register individual tool blueprints with graceful error handling."""
    try:
        # Register the main tools blueprint
        app.register_blueprint(tools_bp)
        print("✅ Tools blueprint registered successfully")
    except Exception as e:
        print(f"❌ Failed to register tools blueprint: {e}")


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


@tools_bp.route("/<slug>/")
def tool_detail(slug):
    """Handle tool detail pages - either redirect to actual tool or show coming soon page."""
    
    # Tool information for creating tool detail pages
    tools_info = {
        # Core Tools
        "seo-audit-tool": {"name": "SEO Audit Tool", "description": "Comprehensive SEO analysis for your website", "category": "Technical SEO"},
        "meta-tag-analyzer": {"name": "Meta Tag Analyzer", "description": "Analyze and optimize your meta tags", "category": "Technical SEO"},
        "page-speed-analyzer": {"name": "Page Speed Analyzer", "description": "Test your website loading speed", "category": "Performance"},
        "keyword-density-analyzer": {"name": "Keyword Density Analyzer", "description": "Analyze keyword density in your content", "category": "Content Analysis"},
        
        # Advanced Tools
        "advanced-keyword-research": {"name": "Advanced Keyword Research", "description": "Advanced keyword research tool", "category": "Keyword Research"},
        "advanced-backlink-analyzer": {"name": "Advanced Backlink Analyzer", "description": "Advanced backlink analysis", "category": "Link Analysis"},
        "technical-seo-analyzer": {"name": "Technical SEO Analyzer", "description": "Comprehensive technical SEO analysis", "category": "Technical SEO"},
        "content-optimizer": {"name": "Content Optimizer", "description": "Optimize content for SEO", "category": "Content Analysis"},
        "schema-generator": {"name": "Schema Generator", "description": "Generate schema markup", "category": "Technical SEO"},
        
        # Technical SEO Tools
        "canonical-tag-checker": {"name": "Canonical Tag Checker", "description": "Check canonical tag implementation", "category": "Technical SEO"},
        "open-graph-preview": {"name": "Open Graph Preview", "description": "Preview Open Graph tags", "category": "Social & Preview"},
        "schema-markup-tester": {"name": "Schema Markup Tester", "description": "Test and validate schema markup", "category": "Technical SEO"},
        "sitemap-xml-validator": {"name": "Sitemap XML Validator", "description": "Validate XML sitemaps", "category": "Technical SEO"},
        "robots-txt-tester": {"name": "Robots.txt Tester", "description": "Test and validate robots.txt file", "category": "Technical SEO"},
        "ssl-checker": {"name": "SSL Checker", "description": "Verify SSL certificate status", "category": "Technical SEO"},
        "http-header-checker": {"name": "HTTP Header Checker", "description": "Analyze HTTP response headers", "category": "Technical SEO"},
        "mobile-optimization-tester": {"name": "Mobile Optimization Tester", "description": "Test mobile optimization", "category": "Performance"},
        "hreflang-tag-checker": {"name": "Hreflang Tag Checker", "description": "Check hreflang tag implementation", "category": "Technical SEO"},
        
        # Content Tools
        "headline-generator": {"name": "Headline Generator", "description": "Generate engaging headlines", "category": "Content Analysis"},
        
        # Link Analysis Tools
        "broken-link-checker": {"name": "Broken Link Checker", "description": "Find and fix broken links", "category": "Link Analysis"},
        "link-status-monitor": {"name": "Link Status Monitor", "description": "Monitor link status", "category": "Link Analysis"},
        "internal-link-analyzer": {"name": "Internal Link Analyzer", "description": "Analyze internal linking structure", "category": "Link Analysis"},
        "redirect-checker": {"name": "Redirect Checker", "description": "Check redirect chains", "category": "Link Analysis"},
        
        # Performance Tools
        "image-compressor": {"name": "Image Compressor", "description": "Compress images for better performance", "category": "Performance"},
        "javascript-minifier": {"name": "JavaScript Minifier", "description": "Minify JavaScript code", "category": "Performance"},
        "core-web-vitals": {"name": "Core Web Vitals", "description": "Measure Core Web Vitals", "category": "Performance"},
        
        # Keyword Research Tools
        "keyword-suggestion-generator": {"name": "Keyword Suggestion Generator", "description": "Generate keyword suggestions", "category": "Keyword Research"},
        "lsi-keyword-generator": {"name": "LSI Keyword Generator", "description": "Generate LSI keywords", "category": "Keyword Research"},
        
        # Technical Tools
        "dns-lookup": {"name": "DNS Lookup", "description": "Perform DNS lookup queries", "category": "Technical Tools"},
        "whois-lookup": {"name": "WHOIS Lookup", "description": "Get domain WHOIS information", "category": "Technical Tools"},
        "password-generator": {"name": "Password Generator", "description": "Generate secure passwords", "category": "Technical Tools"},
        
        # Social & Preview Tools
        "twitter-card-preview": {"name": "Twitter Card Preview", "description": "Preview Twitter cards", "category": "Social & Preview"},
        "social-media-preview": {"name": "Social Media Preview", "description": "Preview social media posts", "category": "Social & Preview"},
    }
    
    # Check if we have info for this tool
    if slug in tools_info:
        tool_info = tools_info[slug]
        
        # Create a tool object for the template
        tool = {
            'name': tool_info['name'],
            'slug': slug,
            'description': tool_info['description'],
            'category': {'name': tool_info['category']},
            'is_premium': False,  # You can adjust this per tool
        }
        
        # Render the tool detail template (coming soon page)
        return render_template('tools/tool_detail.html', tool=tool)
    else:
        # Tool not found
        abort(404)
