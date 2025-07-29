"""
Authentication and authorization decorators for tool access control.
"""

from functools import wraps
from flask import redirect, url_for, flash, jsonify, request
from flask_login import current_user


def login_required_for_tool(f):
    """
    Decorator that requires user to be logged in to access a tool.
    Redirects to login page if not authenticated.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this tool.", "info")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def premium_required(f):
    """
    Decorator that requires user to have premium subscription.
    Redirects to pricing page if not premium.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access premium tools.", "info")
            return redirect(url_for("auth.login"))

        if not current_user.is_premium:
            flash(
                "This is a premium tool. Please upgrade your plan to access advanced features.",
                "warning",
            )
            return redirect(url_for("main.pricing"))

        return f(*args, **kwargs)

    return decorated_function


def check_usage_limit(tool_name, free_limit=5):
    """
    Decorator that checks daily usage limits for free users.
    Premium users have unlimited access.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated and current_user.is_premium:
                # Premium users have unlimited access
                return f(*args, **kwargs)

            # For free/anonymous users, check usage limit
            from flask import session
            from datetime import datetime, date

            # Initialize session data if needed
            if "tool_usage" not in session:
                session["tool_usage"] = {}
            if "usage_date" not in session:
                session["usage_date"] = str(date.today())

            # Reset usage count if it's a new day
            if session["usage_date"] != str(date.today()):
                session["tool_usage"] = {}
                session["usage_date"] = str(date.today())

            # Check current usage for this tool
            current_usage = session["tool_usage"].get(tool_name, 0)

            if current_usage >= free_limit:
                if request.is_json:
                    return (
                        jsonify(
                            {
                                "error": "Daily usage limit reached",
                                "message": f"Free users can use this tool {free_limit} times per day. Please register or upgrade for unlimited access.",
                                "upgrade_url": url_for("main.pricing"),
                            }
                        ),
                        429,
                    )
                else:
                    flash(
                        f"Daily limit reached ({free_limit} uses). Register for more access or upgrade to premium for unlimited usage.",
                        "warning",
                    )
                    return redirect(url_for("main.pricing"))

            # Execute the function
            result = f(*args, **kwargs)

            # Increment usage count after successful execution
            session["tool_usage"][tool_name] = current_usage + 1
            session.permanent = True

            return result

        return decorated_function

    return decorator


def freemium_tool(requires_login=False, is_premium=False, free_limit=5):
    """
    Combined decorator for freemium tool access control.

    Args:
        requires_login: Whether the tool requires user authentication
        is_premium: Whether the tool is premium-only
        free_limit: Daily usage limit for free users (ignored for premium users)
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if login is required
            if requires_login and not current_user.is_authenticated:
                flash("Please log in to access this tool.", "info")
                return redirect(url_for("auth.login"))

            # Check if premium is required
            if is_premium:
                if not current_user.is_authenticated:
                    flash("Please log in to access premium tools.", "info")
                    return redirect(url_for("auth.login"))

                if not current_user.is_premium:
                    flash(
                        "This is a premium tool. Please upgrade your plan to access advanced features.",
                        "warning",
                    )
                    return redirect(url_for("main.pricing"))

            # Check usage limits for non-premium users
            if not (current_user.is_authenticated and current_user.is_premium):
                from flask import session
                from datetime import date

                tool_name = f.__name__

                # Initialize session data if needed
                if "tool_usage" not in session:
                    session["tool_usage"] = {}
                if "usage_date" not in session:
                    session["usage_date"] = str(date.today())

                # Reset usage count if it's a new day
                if session["usage_date"] != str(date.today()):
                    session["tool_usage"] = {}
                    session["usage_date"] = str(date.today())

                # Check current usage for this tool
                current_usage = session["tool_usage"].get(tool_name, 0)

                if current_usage >= free_limit:
                    if request.is_json:
                        return (
                            jsonify(
                                {
                                    "error": "Daily usage limit reached",
                                    "message": f"Free users can use this tool {free_limit} times per day. Please register or upgrade for unlimited access.",
                                    "upgrade_url": url_for("main.pricing"),
                                }
                            ),
                            429,
                        )
                    else:
                        flash(
                            f"Daily limit reached ({free_limit} uses). Register for more access or upgrade to premium for unlimited usage.",
                            "warning",
                        )
                        return redirect(url_for("main.pricing"))

                # Execute the function
                result = f(*args, **kwargs)

                # Increment usage count after successful execution
                session["tool_usage"][tool_name] = current_usage + 1
                session.permanent = True

                return result
            else:
                # Premium users have unlimited access
                return f(*args, **kwargs)

        return decorated_function

    return decorator
