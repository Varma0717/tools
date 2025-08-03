"""Admin module with modular route structure"""

from flask import Blueprint

# Import all admin route blueprints
from .routes.dashboard import dashboard_bp
from .routes.users import users_bp as admin_users_bp
from .routes.content import content_bp
from .routes.analytics import analytics_bp
from .routes.contacts import contacts_bp
from .routes.orders import orders_bp
from .routes.system import system_bp

# Create main admin blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Register all sub-blueprints
def register_admin_routes(app):
    """Register all admin route blueprints with the Flask app"""
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(system_bp)
