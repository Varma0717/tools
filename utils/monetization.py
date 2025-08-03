from functools import wraps
from flask import request, jsonify, redirect, url_for, flash, session
from flask_login import current_user
from models.tool_usage import ToolUsage, Subscription, ToolAnalytics
import re


def get_client_ip():
    """Get client IP address, handling proxies"""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")
    else:
        return request.remote_addr


def extract_tool_name_from_endpoint(endpoint):
    """Extract tool name from Flask endpoint"""
    if not endpoint:
        return "unknown"

    # Handle different endpoint patterns
    if "tools_bp." in endpoint:
        tool_name = endpoint.replace("tools_bp.", "")
    elif "routes." in endpoint:
        tool_name = endpoint.split(".")[-1]
    else:
        tool_name = endpoint

    # Clean up tool name
    tool_name = re.sub(r"[_-]", " ", tool_name).title()
    return tool_name


def get_tool_category(tool_name):
    """Categorize tools for analytics"""
    seo_tools = ["seo", "keyword", "meta", "backlink", "audit", "analysis"]
    content_tools = ["blog", "content", "paraphrase", "generator", "writer"]
    technical_tools = ["minifier", "validator", "speed", "mobile", "javascript"]
    security_tools = ["password", "security", "ssl", "monitor"]

    tool_lower = tool_name.lower()

    if any(word in tool_lower for word in seo_tools):
        return "SEO"
    elif any(word in tool_lower for word in content_tools):
        return "Content"
    elif any(word in tool_lower for word in technical_tools):
        return "Technical"
    elif any(word in tool_lower for word in security_tools):
        return "Security"
    else:
        return "Utility"


def track_tool_usage(f):
    """Decorator to track and limit tool usage"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract tool information
        tool_name = extract_tool_name_from_endpoint(request.endpoint)
        tool_category = get_tool_category(tool_name)
        client_ip = get_client_ip()

        # Get user info
        user_id = current_user.id if current_user.is_authenticated else None
        user_subscription = None

        if user_id:
            subscription = Subscription.get_user_subscription(user_id)
            user_subscription = (
                subscription.plan_type
                if subscription and subscription.is_active
                else None
            )

        # Check usage limits
        can_use, limit_status = ToolUsage.can_use_tool(
            user_id=user_id, ip_address=client_ip, user_subscription=user_subscription
        )

        # Record analytics
        is_premium = user_subscription in ["premium", "enterprise"]
        was_blocked = not can_use

        ToolAnalytics.update_stats(
            tool_name=tool_name,
            is_anonymous=not user_id,
            is_premium=is_premium,
            was_blocked=was_blocked,
        )

        if not can_use:
            # Handle different limit scenarios
            if request.is_json:
                return (
                    jsonify(
                        {
                            "error": True,
                            "message": get_limit_message(limit_status),
                            "upgrade_url": url_for("main.pricing"),
                            "limit_type": limit_status,
                        }
                    ),
                    429,
                )
            else:
                flash(get_limit_message(limit_status), "warning")
                return redirect(url_for("main.pricing"))

        # Record successful usage
        ToolUsage.record_usage(
            tool_name=tool_name,
            tool_category=tool_category,
            user_id=user_id,
            ip_address=client_ip,
            is_premium=is_premium,
        )

        # Execute the original function
        return f(*args, **kwargs)

    return decorated_function


def get_limit_message(limit_status):
    """Get user-friendly limit messages"""
    messages = {
        "daily_limit_reached": "You've reached your daily limit of 1 free tool use. Create an account for 5 monthly uses or upgrade to Premium for unlimited access!",
        "monthly_limit_reached": "You've used all 5 of your monthly tool credits. Upgrade to Premium for unlimited access to all tools!",
        "daily_remaining": "You have 1 free tool use remaining today.",
        "monthly_remaining_4": "You have 4 tool uses remaining this month.",
        "monthly_remaining_3": "You have 3 tool uses remaining this month.",
        "monthly_remaining_2": "You have 2 tool uses remaining this month.",
        "monthly_remaining_1": "You have 1 tool use remaining this month.",
        "unlimited": "Enjoy unlimited access to all tools!",
    }

    return messages.get(limit_status, "Usage limit reached. Please upgrade your plan.")


def require_subscription(min_plan="pro"):
    """Decorator to require specific subscription level"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return (
                        jsonify(
                            {
                                "error": True,
                                "message": "Please log in to access this feature",
                                "login_url": url_for("auth.login"),
                            }
                        ),
                        401,
                    )
                else:
                    flash("Please log in to access this feature", "warning")
                    return redirect(url_for("auth.login"))

            subscription = Subscription.get_user_subscription(current_user.id)

            if not subscription or not subscription.is_active:
                if request.is_json:
                    return (
                        jsonify(
                            {
                                "error": True,
                                "message": f"This feature requires a {min_plan.title()} subscription or higher",
                                "upgrade_url": url_for("main.pricing"),
                            }
                        ),
                        403,
                    )
                else:
                    flash(
                        f"This feature requires a {min_plan.title()} subscription or higher",
                        "warning",
                    )
                    return redirect(url_for("main.pricing"))

            # Check subscription level
            plan_hierarchy = {"pro": 1, "premium": 2, "enterprise": 3}
            user_level = plan_hierarchy.get(subscription.plan_type, 0)
            required_level = plan_hierarchy.get(min_plan, 1)

            if user_level < required_level:
                if request.is_json:
                    return (
                        jsonify(
                            {
                                "error": True,
                                "message": f"This feature requires {min_plan.title()} subscription or higher",
                                "upgrade_url": url_for("main.pricing"),
                            }
                        ),
                        403,
                    )
                else:
                    flash(
                        f"This feature requires {min_plan.title()} subscription or higher",
                        "warning",
                    )
                    return redirect(url_for("main.pricing"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def show_usage_stats():
    """Helper function to get usage stats for current user"""
    if not current_user.is_authenticated:
        client_ip = get_client_ip()
        daily_usage = ToolUsage.get_daily_usage(ip_address=client_ip)
        return {
            "type": "anonymous",
            "daily_usage": daily_usage,
            "daily_limit": 1,
            "monthly_usage": 0,
            "monthly_limit": 0,
            "is_premium": False,
        }

    subscription = Subscription.get_user_subscription(current_user.id)
    is_premium = (
        subscription
        and subscription.is_active
        and subscription.plan_type in ["premium", "enterprise"]
    )

    monthly_usage = ToolUsage.get_monthly_usage(current_user.id)

    return {
        "type": "registered",
        "daily_usage": 0,
        "daily_limit": 0,
        "monthly_usage": monthly_usage,
        "monthly_limit": 5 if not is_premium else float("inf"),
        "is_premium": is_premium,
        "subscription_type": (
            subscription.plan_type if subscription and subscription.is_active else None
        ),
    }
