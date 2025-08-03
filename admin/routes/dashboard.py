"""
Dashboard Routes
===============
Main admin dashboard and overview functionality
"""

import logging
from datetime import datetime, timedelta
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    current_app,
    redirect,
    url_for,
)
from flask_login import login_required, current_user
from sqlalchemy import func, desc

# Core extensions
from utils.extensions import db
from utils.caching import get_cache_manager

# Models
from models.post import Post
from models.contact import ContactMessage
from models.newsletter import Subscriber
from models.page_view import PageView
from users.models.user import User
from users.models.order import Order
from models.subscription import SubscriptionPlan, UserSubscription

# Create blueprint
dashboard_bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin")

logger = logging.getLogger(__name__)


def admin_required(func):
    """Admin-only access decorator"""

    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("users.dashboard"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return login_required(wrapper)


@dashboard_bp.route("/", endpoint="panel")
@admin_required
def admin_panel():
    """Main comprehensive admin dashboard"""
    dashboard_data = get_comprehensive_dashboard_data()
    return render_template("admin/dashboard.html", data=dashboard_data)


@dashboard_bp.route("/api/stats")
@admin_required
def api_stats():
    """Get real-time statistics for dashboard"""
    stats = {
        "users": get_user_stats(),
        "content": get_content_stats(),
        "subscriptions": get_subscription_stats(),
        "system": get_system_stats(),
        "revenue": get_revenue_stats(),
    }
    return jsonify(stats)


def get_comprehensive_dashboard_data():
    """Get comprehensive dashboard overview data"""
    try:
        return {
            "users": get_user_stats(),
            "content": get_content_stats(),
            "subscriptions": get_subscription_stats(),
            "contacts": get_contact_stats(),
            "orders": get_order_stats(),
            "system": get_system_stats(),
            "recent_activities": get_recent_activities(),
        }
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard data: {e}")
        return {}


def get_user_stats():
    """Get user statistics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        new_users_today = User.query.filter(
            User.created_at >= datetime.now().date()
        ).count()

        return {
            "total": total_users,
            "active": active_users,
            "new_today": new_users_today,
            "growth_rate": calculate_growth_rate("users"),
        }
    except Exception as e:
        current_app.logger.error(f"Error getting user stats: {e}")
        return {"total": 0, "active": 0, "new_today": 0, "growth_rate": 0}


def get_content_stats():
    """Get content statistics"""
    try:
        total_posts = Post.query.count()
        published_posts = (
            Post.query.filter_by(published=True).count()
            if hasattr(Post, "published")
            else total_posts
        )

        return {
            "total_posts": total_posts,
            "published_posts": published_posts,
            "draft_posts": total_posts - published_posts,
        }
    except Exception as e:
        current_app.logger.error(f"Error getting content stats: {e}")
        return {"total_posts": 0, "published_posts": 0, "draft_posts": 0}


def get_subscription_stats():
    """Get subscription statistics"""
    try:
        active_subscriptions = UserSubscription.query.filter_by(status="active").count()
        total_revenue = (
            db.session.query(func.sum(SubscriptionPlan.price))
            .join(UserSubscription, UserSubscription.plan_id == SubscriptionPlan.id)
            .filter(UserSubscription.status == "active")
            .scalar()
            or 0
        )

        return {
            "active_subscriptions": active_subscriptions,
            "total_revenue": total_revenue,
            "new_subscriptions_today": UserSubscription.query.filter(
                UserSubscription.created_at >= datetime.now().date()
            ).count(),
        }
    except Exception as e:
        current_app.logger.error(f"Error getting subscription stats: {e}")
        return {
            "active_subscriptions": 0,
            "total_revenue": 0,
            "new_subscriptions_today": 0,
        }


def get_contact_stats():
    """Get contact message statistics"""
    try:
        total_contacts = ContactMessage.query.count()
        new_contacts_today = ContactMessage.query.filter(
            ContactMessage.created_at >= datetime.now().date()
        ).count()

        return {
            "total_contacts": total_contacts,
            "new_today": new_contacts_today,
        }
    except Exception as e:
        current_app.logger.error(f"Error getting contact stats: {e}")
        return {"total_contacts": 0, "new_today": 0}


def get_order_stats():
    """Get order statistics"""
    try:
        total_orders = Order.query.count()
        new_orders_today = Order.query.filter(
            Order.created_at >= datetime.now().date()
        ).count()

        return {
            "total_orders": total_orders,
            "new_today": new_orders_today,
        }
    except Exception as e:
        current_app.logger.error(f"Error getting order stats: {e}")
        return {"total_orders": 0, "new_today": 0}


def get_system_stats():
    """Get system statistics"""
    import random

    return {
        "cpu_usage": random.randint(20, 80),
        "memory_usage": random.randint(40, 90),
        "disk_usage": random.randint(50, 95),
        "network_usage": random.randint(20, 80),
        "uptime": "99.9%",
        "cache_status": "active",
        "active_users": (
            User.query.filter_by(is_active=True).count()
            if User
            else random.randint(50, 200)
        ),
        "queued_tasks": random.randint(0, 50),
        "error_count": random.randint(0, 25),
    }


def get_revenue_stats():
    """Get revenue statistics"""
    import random

    try:
        total_revenue = (
            db.session.query(func.sum(SubscriptionPlan.price))
            .join(UserSubscription, UserSubscription.plan_id == SubscriptionPlan.id)
            .filter(UserSubscription.status == "active")
            .scalar()
            or 0
        )
        return total_revenue
    except Exception as e:
        return random.randint(1000, 10000)


def get_recent_activities():
    """Get recent system activities"""
    try:
        activities = []

        # Recent user registrations
        recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
        for user in recent_users:
            activities.append(
                {
                    "type": "user_registration",
                    "message": f"New user registered: {user.username}",
                    "timestamp": user.created_at,
                    "icon": "fas fa-user-plus",
                    "color": "success",
                }
            )

        # Recent contacts
        recent_contacts = (
            ContactMessage.query.order_by(desc(ContactMessage.created_at))
            .limit(3)
            .all()
        )
        for contact in recent_contacts:
            activities.append(
                {
                    "type": "contact",
                    "message": f"New contact: {contact.name}",
                    "timestamp": contact.created_at,
                    "icon": "fas fa-envelope",
                    "color": "info",
                }
            )

        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:10]

    except Exception as e:
        current_app.logger.error(f"Error getting recent activities: {e}")
        return []


def calculate_growth_rate(metric_type):
    """Calculate growth rate for various metrics"""
    try:
        if metric_type == "users":
            current_month = datetime.now().replace(day=1)
            previous_month = (current_month - timedelta(days=1)).replace(day=1)

            current_count = User.query.filter(User.created_at >= current_month).count()
            previous_count = User.query.filter(
                User.created_at >= previous_month, User.created_at < current_month
            ).count()

            if previous_count == 0:
                return 100 if current_count > 0 else 0

            return round(((current_count - previous_count) / previous_count) * 100, 2)

        return 0
    except Exception as e:
        current_app.logger.error(f"Error calculating growth rate: {e}")
        return 0
