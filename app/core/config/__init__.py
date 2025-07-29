"""
Application configuration classes.
"""

import os
from typing import Optional


class Config:
    """Base configuration class."""

    # Basic Flask Config
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Database - MySQL configuration
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "mysql+pymysql://root:@localhost/test"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}

    # Mail Configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in [
        "true",
        "1",
        "yes",
    ]
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() in [
        "true",
        "1",
        "yes",
    ]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")

    # API Keys
    OPENROUTER_API_KEYS = [
        k.strip()
        for k in os.environ.get("OPENROUTER_API_KEYS", "").split(",")
        if k.strip()
    ]

    # PayPal Configuration
    PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET")
    PAYPAL_ENVIRONMENT = os.environ.get("PAYPAL_ENVIRONMENT", "sandbox")

    # Stripe Configuration
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

    # Site Settings
    SITE_URL = os.environ.get("YOUR_SITE_URL", "http://localhost:5000")
    SITE_NAME = os.environ.get("YOUR_SITE_NAME", "Super SEO Toolkit")

    # Security Settings
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = "static/uploads"


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False

    # Development database - Use MySQL for all environments
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL") or "mysql+pymysql://root:@localhost/test"
    )

    # Disable CSRF for easier development
    WTF_CSRF_ENABLED = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Production database - MySQL with enhanced configuration
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '3306')}/{os.environ.get('DB_NAME', 'super_seo_toolkit')}?charset=utf8mb4"
    )

    # Production MySQL optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }  # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = False
    TESTING = True

    # MySQL database for testing (you may want to use a separate test database)
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/test_db"

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Disable mail sending during tests
    MAIL_SUPPRESS_SEND = True


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration class based on environment.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Configuration class instance
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    return config.get(config_name, config["default"])
