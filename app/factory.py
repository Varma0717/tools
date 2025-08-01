"""
Application factory and Flask app creation.
Production-ready Flask application factory with improved structure.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from flask import Flask
from flask_dance.contrib.google import make_google_blueprint

from app.core.config import get_config
from app.core.extensions import db, login_manager, mail, migrate, csrf
from app.core.error_handlers import register_error_handlers


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure Flask application using the application factory pattern.

    Args:
        config_name: Configuration environment name ('development', 'production', 'testing')

    Returns:
        Configured Flask application instance
    """
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates",
        instance_relative_config=True,
    )

    # Load configuration
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    _init_extensions(app)

    # Configure logging
    _configure_logging(app)

    # Set up OAuth
    _setup_oauth(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        _import_models()

    return app


def _init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Configure user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User

        return User.query.get(int(user_id))

    # Add CSRF token to template context globally
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf

        return dict(csrf_token=generate_csrf())

    # Add categories to template context globally for navigation
    @app.context_processor
    def inject_categories():
        # Static categories matching tools page
        categories = [
            {"name": "Technical SEO", "slug": "technical-seo", "icon": "search"},
            {"name": "Performance", "slug": "performance", "icon": "zap"},
            {
                "name": "Content Analysis",
                "slug": "content-analysis",
                "icon": "file-text",
            },
            {"name": "Keyword Research", "slug": "keyword-research", "icon": "target"},
            {"name": "Link Analysis", "slug": "link-analysis", "icon": "link"},
            {"name": "Technical Tools", "slug": "technical-tools", "icon": "tool"},
        ]
        return dict(nav_categories=categories)


def _configure_logging(app: Flask) -> None:
    """Configure application logging."""
    if not app.debug and not app.testing:
        if not os.path.exists("logs"):
            os.mkdir("logs")

        file_handler = RotatingFileHandler(
            "logs/flask_app.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Super SEO Toolkit startup")


def _setup_oauth(app: Flask) -> None:
    """Set up OAuth blueprints."""
    google_bp = make_google_blueprint(
        client_id=app.config.get("GOOGLE_CLIENT_ID"),
        client_secret=app.config.get("GOOGLE_CLIENT_SECRET"),
        scope=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
    )
    app.register_blueprint(google_bp, url_prefix="/login")


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""

    # Main routes
    from app.blueprints.main import main_bp

    app.register_blueprint(main_bp)

    # User routes
    from app.blueprints.users import users_bp

    app.register_blueprint(users_bp)

    # Admin routes
    from app.blueprints.admin import admin_bp

    app.register_blueprint(admin_bp)

    # Auth routes
    from app.blueprints.auth import auth_bp

    app.register_blueprint(auth_bp)

    # Tools routes - Now using modular routing system
    from app.blueprints.tools import register_all_tool_blueprints

    # Register all tool blueprints (main index + all 8 categories)
    register_all_tool_blueprints(app)

    # API routes
    from app.blueprints.api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    # Blog routes
    from app.blueprints.blog import blog_bp

    app.register_blueprint(blog_bp)

    # Contact routes
    from app.blueprints.blog.contact import contact_bp

    app.register_blueprint(contact_bp)

    # Payment routes
    from app.blueprints.payment import payment_bp

    app.register_blueprint(payment_bp)

    # Routes routes (if exists)
    try:
        from app.blueprints.routes import routes_bp

        app.register_blueprint(routes_bp)
    except ImportError:
        pass  # routes blueprint might not exist


def _import_models() -> None:
    """Import all models to register them with SQLAlchemy."""
    from app.models import (
        User,
        Contact,
        FAQ,
        Newsletter,
        Subscriber,
        PageView,
        Post,
        Subscription,
        Testimonial,
        Setting,
    )
