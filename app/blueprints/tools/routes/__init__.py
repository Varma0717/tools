"""
Route Manager - Automatically registers all tool route blueprints
This approach scales to 100+ tools without bloating main_routes.py
"""

from .seo_tools import seo_tools_bp


def register_tool_routes(app):
    """
    Register all tool route blueprints

    This modular approach allows for:
    - 100+ tools without bloating single files
    - Easy maintenance and debugging
    - Team development (different devs work on different route files)
    - Clear separation of concerns
    - Fast loading and better performance
    """

    # Register all tool blueprints (only existing ones for now)
    tool_blueprints = [
        seo_tools_bp,  # /tools/seo/*
        # Future blueprints will be added here as we create them:
        # content_tools_bp,  # /tools/content/*
        # keyword_tools_bp,  # /tools/keywords/*
        # link_tools_bp,     # /tools/links/*
    ]

    registered_count = 0
    for blueprint in tool_blueprints:
        app.register_blueprint(blueprint)
        registered_count += 1

    print(f"✅ Registered {registered_count} tool route blueprints")

    # Future blueprints can be added here:
    # - social_tools_bp    # /tools/social/*
    # - analytics_tools_bp # /tools/analytics/*
    # - security_tools_bp  # /tools/security/*
    # - image_tools_bp     # /tools/images/*
    # - performance_tools_bp # /tools/performance/*
    # etc...

    return registered_count


# Route mapping for URL redirects (maintains backward compatibility)
ROUTE_MAPPING = {
    # Old routes -> New routes
    "tools.tools_seo_audit_tool": "seo_tools.seo_audit_tool",
    "tools.tools_analyze_seo": "seo_tools.analyze_seo",
    "tools.seo_reports_history": "seo_tools.seo_reports_history",
    "tools.view_seo_report": "seo_tools.view_seo_report",
    "tools.download_seo_report_pdf": "seo_tools.download_seo_report_pdf",
}
# allowing imports like: from app.blueprints.tools.routes.tool_name import tool_bp
