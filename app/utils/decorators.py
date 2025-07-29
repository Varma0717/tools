"""
Utility decorators for Flask application.
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Decorator to require admin role."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def premium_required(f):
    """Decorator to require premium subscription."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_premium:
            flash("Premium subscription required.", "warning")
            return redirect(url_for("main.pricing"))
        return f(*args, **kwargs)

    return decorated_function


def anonymous_required(f):
    """Decorator to require anonymous user (not logged in)."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)

    return decorated_function
