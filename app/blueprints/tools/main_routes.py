"""
Simplified tools blueprint - SEO Audit Tool ONLY
"""

from flask import Blueprint, render_template

# Create the main tools blueprint
tools_bp = Blueprint("tools", __name__, url_prefix="/tools")


def register_tool_blueprints(app):
    """Register only the SEO audit tool blueprint."""
    
    try:
        # Import and register only the SEO audit tool
        from app.blueprints.tools.routes.seo_audit_tool import seo_audit_tool_bp
        app.register_blueprint(seo_audit_tool_bp)
        print("✅ SEO Audit Tool registered successfully")
        return 1
    except Exception as e:
        print(f"❌ Failed to register SEO Audit Tool: {str(e)}")
        return 0


@tools_bp.route("/")
def tools_index():
    """Main tools page showing only SEO Audit Tool."""

    # Only SEO Audit Tool data
    tools_data = {
        "Technical SEO": [
            {
                "name": "SEO Audit Tool",
                "slug": "seo-audit-tool",
                "description": "Comprehensive SEO analysis for your website with unlimited page crawling and detailed insights",
                "is_premium": False,
                "category": {"name": "Technical SEO"},
            }
        ]
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

    return render_template(
        "tools/index.html",
        tools_data=tools_data,
        tools_by_category=tools_data,  # Also pass as expected name
        tools=all_tools,  # Add flattened tools list
        categories=categories,
        total_tools=total_tools,
    )


# No other tool routes - only SEO Audit Tool exists