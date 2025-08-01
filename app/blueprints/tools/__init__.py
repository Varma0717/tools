"""
Tools blueprint for SEO tools.
"""

from .main_routes import tools_bp, register_tool_blueprints

# Import all category blueprints
from .routes.seo_tools import seo_tools_bp
from .routes.premium_seo_routes import premium_seo_bp
from .routes.content_tools import content_tools_bp
from .routes.keyword_tools import keyword_tools_bp
from .routes.link_tools import link_tools_bp
from .routes.performance_tools import performance_tools_bp
from .routes.technical_tools import technical_tools_bp
from .routes.social_tools import social_tools_bp
from .routes.analytics_tools import analytics_tools_bp
from .routes.security_tools import security_tools_bp


# Register all category blueprints
def register_all_tool_blueprints(app):
    """Register all tool category blueprints"""
    app.register_blueprint(tools_bp)
    app.register_blueprint(seo_tools_bp)
    app.register_blueprint(premium_seo_bp)
    app.register_blueprint(content_tools_bp)
    app.register_blueprint(keyword_tools_bp)
    app.register_blueprint(link_tools_bp)
    app.register_blueprint(performance_tools_bp)
    app.register_blueprint(technical_tools_bp)
    app.register_blueprint(social_tools_bp)
    app.register_blueprint(analytics_tools_bp)
    app.register_blueprint(security_tools_bp)


__all__ = ["tools_bp", "register_tool_blueprints", "register_all_tool_blueprints"]
