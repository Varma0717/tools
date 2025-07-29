"""
Tools-specific decorators and utilities.
"""

from functools import wraps
from flask import redirect, url_for, flash, request, jsonify
from flask_login import current_user


def tool_login_required(f):
    """
    Decorator to require login for tool access.
    TEMPORARILY DISABLED - Tools are now free for everyone.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Temporarily disable login requirement - tools are free for everyone
        return f(*args, **kwargs)

        # Original login check (disabled):
        # if not current_user.is_authenticated:
        #     flash("Please log in to access SEO tools.", "info")
        #     return redirect(url_for("users.login", next=request.url))
        # return f(*args, **kwargs)

    return decorated_function


def premium_tool_required(f):
    """
    Decorator to require premium access for AI writing tools.
    Checks for Pro subscription or allows 5 free uses per month.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access AI writing tools.", "info")
            return redirect(url_for("auth.login", next=request.url))

        # Admin always has access
        if current_user.is_admin():
            return f(*args, **kwargs)

        # Check if user has pro subscription
        if current_user.has_pro_subscription():
            return f(*args, **kwargs)

        # Check free tier usage limit (5 uses per month)
        monthly_usage = current_user.get_ai_tool_usage_this_month()
        if monthly_usage >= 5:
            if request.is_json:
                return (
                    jsonify(
                        {
                            "error": "Monthly AI tool limit reached. Upgrade to Pro for unlimited access.",
                            "upgrade_required": True,
                        }
                    ),
                    403,
                )
            else:
                flash(
                    "You've reached your monthly limit of 5 AI tool uses. Upgrade to Pro for unlimited access!",
                    "warning",
                )
                return redirect(url_for("main.pricing"))

        # Record usage for free tier
        from app.models.subscription import AIToolUsage

        tool_name = f.__name__.replace("_ajax", "").replace("_", "-")
        AIToolUsage.record_usage(current_user.id, tool_name)

        return f(*args, **kwargs)

    return decorated_function


def admin_tool_required(f):
    """
    Decorator to require admin access for admin-only tools.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access admin tools.", "info")
            return redirect(url_for("auth.login", next=request.url))

        if current_user.role != "admin":
            flash("Admin access required for this tool.", "error")
            return redirect(url_for("main.home"))

        return f(*args, **kwargs)

    return decorated_function
