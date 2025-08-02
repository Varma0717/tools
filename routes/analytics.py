from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from models.subscription import UsageTracking, UserSubscription
from models.post import Post
from models.newsletter import Subscriber
from utils.decorators import admin_required
import json

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/dashboard")
@login_required
def dashboard():
    """Main analytics dashboard"""
    if current_user.role == "admin":
        return render_template("analytics/admin_dashboard.html")
    else:
        return render_template("analytics/user_dashboard.html")


@analytics_bp.route("/api/user-stats")
@login_required
def user_stats_api():
    """API endpoint for user statistics"""
    user_id = current_user.id

    # Get usage data for last 30 days
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)

    # Daily usage over last 30 days
    daily_usage = (
        db.session.query(
            UsageTracking.usage_date,
            func.sum(UsageTracking.usage_count).label("total_usage"),
        )
        .filter(
            UsageTracking.user_id == user_id,
            UsageTracking.usage_date >= thirty_days_ago,
        )
        .group_by(UsageTracking.usage_date)
        .all()
    )

    # Top used tools
    top_tools = (
        db.session.query(
            UsageTracking.tool_name,
            func.sum(UsageTracking.usage_count).label("usage_count"),
        )
        .filter(
            UsageTracking.user_id == user_id,
            UsageTracking.usage_date >= thirty_days_ago,
        )
        .group_by(UsageTracking.tool_name)
        .order_by(desc("usage_count"))
        .limit(10)
        .all()
    )

    # Current subscription info
    subscription = UserSubscription.query.filter_by(
        user_id=user_id, status="active"
    ).first()

    return jsonify(
        {
            "daily_usage": [
                {"date": usage.usage_date.isoformat(), "count": usage.total_usage}
                for usage in daily_usage
            ],
            "top_tools": [
                {"tool": tool.tool_name, "usage": tool.usage_count}
                for tool in top_tools
            ],
            "subscription": {
                "plan": subscription.plan.name if subscription else "Free",
                "status": subscription.status if subscription else "free",
                "days_remaining": (
                    subscription.days_remaining() if subscription else None
                ),
                "daily_limit": (
                    subscription.plan.max_daily_usage if subscription else 10
                ),
            },
            "today_usage": UsageTracking.get_daily_usage(user_id),
        }
    )


@analytics_bp.route("/api/admin-stats")
@login_required
@admin_required
def admin_stats_api():
    """API endpoint for admin statistics"""

    # Total users
    total_users = User.query.count()

    # Active subscriptions
    active_subscriptions = UserSubscription.query.filter_by(status="active").count()

    # Revenue calculation (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_subscriptions = UserSubscription.query.filter(
        UserSubscription.created_at >= thirty_days_ago
    ).all()

    monthly_revenue = sum([sub.plan.price for sub in recent_subscriptions])

    # Most popular tools
    popular_tools = (
        db.session.query(
            UsageTracking.tool_name,
            func.sum(UsageTracking.usage_count).label("total_usage"),
        )
        .group_by(UsageTracking.tool_name)
        .order_by(desc("total_usage"))
        .limit(10)
        .all()
    )

    # User growth (last 12 months)
    user_growth = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)

        count = User.query.filter(
            User.created_at >= month_start, User.created_at < month_end
        ).count()

        user_growth.append({"month": month_start.strftime("%Y-%m"), "new_users": count})

    return jsonify(
        {
            "overview": {
                "total_users": total_users,
                "active_subscriptions": active_subscriptions,
                "monthly_revenue": monthly_revenue,
                "total_posts": Post.query.count(),
                "newsletter_subscribers": Subscriber.query.count(),
            },
            "popular_tools": [
                {"tool": tool.tool_name, "usage": tool.total_usage}
                for tool in popular_tools
            ],
            "user_growth": list(reversed(user_growth)),
        }
    )


@analytics_bp.route("/api/revenue-stats")
@login_required
@admin_required
def revenue_stats_api():
    """API endpoint for revenue analytics"""

    # Monthly revenue for last 12 months
    monthly_revenue = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)

        subscriptions = UserSubscription.query.filter(
            UserSubscription.created_at >= month_start,
            UserSubscription.created_at < month_end,
            UserSubscription.status.in_(["active", "cancelled"]),
        ).all()

        revenue = sum([sub.plan.price for sub in subscriptions])

        monthly_revenue.append(
            {
                "month": month_start.strftime("%Y-%m"),
                "revenue": revenue,
                "subscriptions_count": len(subscriptions),
            }
        )

    # Subscription distribution
    subscription_distribution = (
        db.session.query(
            SubscriptionPlan.name,
            func.count(UserSubscription.id).label("count"),
            SubscriptionPlan.price,
        )
        .join(UserSubscription)
        .filter(UserSubscription.status == "active")
        .group_by(SubscriptionPlan.name, SubscriptionPlan.price)
        .all()
    )

    return jsonify(
        {
            "monthly_revenue": list(reversed(monthly_revenue)),
            "subscription_distribution": [
                {
                    "plan": dist.name,
                    "count": dist.count,
                    "price": dist.price,
                    "revenue": dist.count * dist.price,
                }
                for dist in subscription_distribution
            ],
        }
    )


@analytics_bp.route("/reports/usage")
@login_required
def usage_report():
    """Detailed usage report page"""
    return render_template("analytics/usage_report.html")


@analytics_bp.route("/reports/performance")
@login_required
@admin_required
def performance_report():
    """System performance report"""
    return render_template("analytics/performance_report.html")
