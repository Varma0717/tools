"""
Admin Routes Module
==================
This module contains all admin routes organized by functionality.
"""

from .dashboard import dashboard_bp
from .users import users_bp
from .content import content_bp
from .analytics import analytics_bp
from .system import system_bp
from .orders import orders_bp
from .contacts import contacts_bp
from .api_management import api_bp
from .security import security_bp
from .insights import insights_bp
from .communications import communications_bp

# Export all blueprints for easy importing
__all__ = [
    "dashboard_bp",
    "users_bp",
    "content_bp",
    "analytics_bp",
    "system_bp",
    "orders_bp",
    "contacts_bp",
    "api_bp",
    "security_bp",
    "insights_bp",
    "communications_bp",
]
