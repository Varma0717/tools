from functools import wraps
from flask import redirect, url_for, flash, request, jsonify
from flask_login import current_user


def login_required_infrastructure(f):
    """
    Professional infrastructure decorator that requires login for all tools
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if (
                request.is_json
                or request.headers.get("Content-Type") == "application/json"
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Authentication required for professional tools",
                            "redirect": url_for("auth.login"),
                        }
                    ),
                    401,
                )
            flash("Please login to access professional developer tools.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def pro_subscription_required(f):
    """
    Decorator for AI tools that require Pro subscription
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Authentication required",
                            "redirect": url_for("auth.login"),
                        }
                    ),
                    401,
                )
            return redirect(url_for("auth.login", next=request.url))

        if not current_user.has_active_subscription():
            if request.is_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Pro subscription required for AI-powered tools",
                            "upgrade_url": url_for("subscription.pricing"),
                        }
                    ),
                    403,
                )
            flash("This AI-powered tool requires a Pro subscription.", "info")
            return redirect(url_for("subscription.pricing"))
        return f(*args, **kwargs)

    return decorated_function


def openrouter_api_tool(f):
    """
    Decorator for tools that use OpenRouter API and require payment
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check authentication
        if not current_user.is_authenticated:
            if request.is_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Authentication required",
                            "redirect": url_for("auth.login"),
                        }
                    ),
                    401,
                )
            return redirect(url_for("auth.login", next=request.url))

        # Check subscription for AI tools
        if not current_user.has_active_subscription():
            if request.is_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Pro subscription required for AI-powered analysis",
                            "upgrade_url": url_for("subscription.pricing"),
                        }
                    ),
                    403,
                )
            flash("AI-powered tools require a Pro subscription.", "info")
            return redirect(url_for("subscription.pricing"))
        return f(*args, **kwargs)

    return decorated_function
