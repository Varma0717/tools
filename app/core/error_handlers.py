"""
Application error handlers.
"""

from flask import Flask, render_template, request
import logging


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the application."""

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        app.logger.warning(f"404 error: {request.url}")
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors."""
        app.logger.warning(f"403 error: {request.url}")
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        app.logger.error(f"500 error: {error}", exc_info=True)
        return render_template("errors/500.html"), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        """Handle CSRF token errors."""
        app.logger.warning(f"CSRF error: {error.description}")
        return render_template("errors/csrf.html"), 400


# Import CSRF error after extensions are available
try:
    from flask_wtf.csrf import CSRFError
except ImportError:
    # Fallback if CSRFError is not available
    class CSRFError(Exception):
        def __init__(self, description="CSRF token missing or invalid"):
            self.description = description
