"""
Simplified tools blueprint - basic functionality only.
"""

from .main_routes import tools_bp


def register_all_tool_blueprints(app):
    """Register the simplified tools blueprint"""
    app.register_blueprint(tools_bp)
    return 1  # Only one blueprint now
    app.register_blueprint(social_tools_bp)
    app.register_blueprint(analytics_tools_bp)
    app.register_blueprint(security_tools_bp)


__all__ = ["tools_bp", "register_tool_blueprints", "register_all_tool_blueprints"]
