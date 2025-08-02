from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from models.subscription import UsageTracking, UserSubscription, SubscriptionPlan
from models.crm import (
    Lead,
    CustomerInteraction,
    CRMAnalytics,
    BusinessMetrics,
    UserBehavior,
    CampaignTracking,
    CustomerSegment,
    UserSegmentMembership,
)
from models.post import Post
from models.newsletter import Subscriber
from models.contact import ContactMessage
from users.models.user import User
from utils.decorators import admin_required
from utils.extensions import db
from utils.crm_analytics import get_conversion_funnel_data, CRMInsights
import json

crm_bp = Blueprint("crm", __name__, url_prefix="/crm")


@crm_bp.route("/dashboard")
@login_required
def dashboard():
    """CRM Dashboard with role-based access"""
    if current_user.role == "admin":
        return render_template("crm/admin_crm_dashboard.html")
    else:
        return render_template("crm/user_crm_dashboard.html")


@crm_bp.route("/api/admin-crm-stats")
@login_required
@admin_required
def admin_crm_stats():
    """Comprehensive admin CRM statistics"""
    try:
        # Date ranges
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)

        # Core Metrics
        total_users = User.query.count()
        active_subscribers = UserSubscription.query.filter_by(status="active").count()
        total_leads = Lead.query.count()
        converted_leads = Lead.query.filter_by(status="converted").count()

        # Revenue Metrics
        monthly_revenue = (
            db.session.query(func.sum(SubscriptionPlan.price))
            .join(UserSubscription, UserSubscription.plan_id == SubscriptionPlan.id)
            .filter(UserSubscription.status == "active")
            .scalar()
            or 0
        )

        # Growth Metrics
        users_growth = calculate_growth_rate(User, "id", month_ago)
        subscribers_growth = calculate_growth_rate(
            UserSubscription, "id", month_ago, status="active"
        )
        leads_growth = calculate_growth_rate(Lead, "id", month_ago)

        # Tool Usage
        daily_tool_usage = UsageTracking.query.filter(
            UsageTracking.usage_date == today
        ).count()

        # Customer Satisfaction
        avg_satisfaction = (
            db.session.query(func.avg(CustomerInteraction.satisfaction_rating))
            .filter(CustomerInteraction.satisfaction_rating.isnot(None))
            .scalar()
            or 0
        )

        # Lead Sources
        lead_sources = (
            db.session.query(Lead.source, func.count(Lead.id).label("count"))
            .group_by(Lead.source)
            .all()
        )

        # Conversion Funnel
        conversion_funnel = {
            "leads": total_leads,
            "qualified": Lead.query.filter_by(status="qualified").count(),
            "customers": converted_leads,
            "active_customers": active_subscribers,
        }

        # Recent Activities
        recent_leads = Lead.query.order_by(desc(Lead.created_at)).limit(5).all()
        recent_interactions = (
            CustomerInteraction.query.order_by(desc(CustomerInteraction.created_at))
            .limit(5)
            .all()
        )

        # Top Performing Tools
        top_tools = (
            db.session.query(
                UsageTracking.tool_name,
                func.sum(UsageTracking.usage_count).label("usage"),
                func.count(func.distinct(UsageTracking.user_id)).label("unique_users"),
            )
            .filter(UsageTracking.usage_date >= month_ago)
            .group_by(UsageTracking.tool_name)
            .order_by(desc("usage"))
            .limit(10)
            .all()
        )

        # Customer Segments
        segments = CustomerSegment.query.filter_by(is_active=True).all()
        segment_data = []
        for segment in segments:
            count = (
                db.session.query(func.count())
                .select_from(
                    User.query.join(UserSegmentMembership)
                    .filter(UserSegmentMembership.segment_id == segment.id)
                    .subquery()
                )
                .scalar()
            )
            segment_data.append(
                {"name": segment.name, "count": count, "color": segment.color}
            )

        # Revenue Trend (last 12 months)
        revenue_trend = []
        for i in range(12):
            month_start = today - timedelta(days=30 * (i + 1))
            month_end = today - timedelta(days=30 * i)

            month_revenue = (
                db.session.query(func.sum(SubscriptionPlan.price))
                .join(UserSubscription, UserSubscription.plan_id == SubscriptionPlan.id)
                .filter(
                    and_(
                        UserSubscription.status == "active",
                        UserSubscription.start_date >= month_start,
                        UserSubscription.start_date < month_end,
                    )
                )
                .scalar()
                or 0
            )

            revenue_trend.append(
                {
                    "month": month_start.strftime("%b %Y"),
                    "revenue": float(month_revenue),
                }
            )

        revenue_trend.reverse()

        # User Acquisition Trend
        user_trend = []
        for i in range(30):
            date = today - timedelta(days=i)
            count = User.query.filter(func.date(User.created_at) == date).count()
            user_trend.append({"date": date.isoformat(), "users": count})
        user_trend.reverse()

        return jsonify(
            {
                "success": True,
                "metrics": {
                    "total_users": total_users,
                    "active_subscribers": active_subscribers,
                    "total_leads": total_leads,
                    "conversion_rate": round(
                        (converted_leads / total_leads * 100) if total_leads > 0 else 0,
                        2,
                    ),
                    "monthly_revenue": monthly_revenue,
                    "daily_tool_usage": daily_tool_usage,
                    "avg_satisfaction": round(float(avg_satisfaction), 2),
                    "churn_rate": round(CRMAnalytics.get_churn_rate(), 2),
                    "customer_lifetime_value": round(
                        CRMAnalytics.get_customer_lifetime_value(), 2
                    ),
                },
                "growth": {
                    "users_growth": users_growth,
                    "subscribers_growth": subscribers_growth,
                    "leads_growth": leads_growth,
                },
                "charts": {
                    "revenue_trend": revenue_trend,
                    "user_trend": user_trend,
                    "lead_sources": [
                        {"source": ls.source or "Direct", "count": ls.count}
                        for ls in lead_sources
                    ],
                    "conversion_funnel": conversion_funnel,
                    "segment_distribution": segment_data,
                },
                "top_tools": [
                    {
                        "name": tool.tool_name,
                        "usage": tool.usage,
                        "unique_users": tool.unique_users,
                    }
                    for tool in top_tools
                ],
                "recent_activity": {
                    "leads": [
                        {
                            "name": lead.name or lead.email,
                            "source": lead.source,
                            "status": lead.status,
                            "created_at": lead.created_at.strftime("%Y-%m-%d %H:%M"),
                        }
                        for lead in recent_leads
                    ],
                    "interactions": [
                        {
                            "user": (
                                interaction.user.username
                                if interaction.user
                                else "Unknown"
                            ),
                            "type": interaction.interaction_type,
                            "status": interaction.status,
                            "created_at": interaction.created_at.strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                        }
                        for interaction in recent_interactions
                    ],
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@crm_bp.route("/api/user-crm-stats")
@login_required
def user_crm_stats():
    """User-specific CRM statistics"""
    try:
        user_id = current_user.id
        today = datetime.utcnow().date()
        month_ago = today - timedelta(days=30)

        # User's subscription info
        subscription = UserSubscription.query.filter_by(
            user_id=user_id, status="active"
        ).first()

        # Usage statistics
        total_usage = UsageTracking.query.filter_by(user_id=user_id).count()
        monthly_usage = UsageTracking.query.filter(
            UsageTracking.user_id == user_id, UsageTracking.usage_date >= month_ago
        ).count()

        daily_usage = UsageTracking.get_daily_usage(user_id)
        daily_limit = subscription.plan.max_daily_usage if subscription else 10

        # Tool preferences
        top_tools = (
            db.session.query(
                UsageTracking.tool_name,
                func.sum(UsageTracking.usage_count).label("usage"),
            )
            .filter(UsageTracking.user_id == user_id)
            .group_by(UsageTracking.tool_name)
            .order_by(desc("usage"))
            .limit(5)
            .all()
        )

        # Usage trend (last 30 days)
        usage_trend = []
        for i in range(30):
            date = today - timedelta(days=i)
            count = UsageTracking.query.filter(
                UsageTracking.user_id == user_id, UsageTracking.usage_date == date
            ).count()
            usage_trend.append({"date": date.isoformat(), "usage": count})
        usage_trend.reverse()

        # Account metrics
        account_age = (datetime.utcnow().date() - current_user.created_at.date()).days

        return jsonify(
            {
                "success": True,
                "user_info": {
                    "username": current_user.username,
                    "email": current_user.email,
                    "account_age_days": account_age,
                    "is_premium": current_user.is_premium or (subscription is not None),
                },
                "subscription": {
                    "plan": subscription.plan.name if subscription else "Free",
                    "status": subscription.status if subscription else "free",
                    "end_date": (
                        subscription.end_date.isoformat() if subscription else None
                    ),
                    "daily_limit": daily_limit,
                    "monthly_limit": (
                        subscription.plan.max_reports if subscription else 5
                    ),
                },
                "usage": {
                    "daily_usage": daily_usage,
                    "daily_limit": daily_limit,
                    "monthly_usage": monthly_usage,
                    "total_usage": total_usage,
                    "usage_percentage": round((daily_usage / daily_limit * 100), 2),
                },
                "charts": {
                    "usage_trend": usage_trend,
                    "top_tools": [
                        {"tool": tool.tool_name, "usage": tool.usage}
                        for tool in top_tools
                    ],
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@crm_bp.route("/leads")
@login_required
@admin_required
def leads():
    """Lead management page"""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    leads = Lead.query.order_by(desc(Lead.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template("crm/leads.html", leads=leads)


@crm_bp.route("/interactions")
@login_required
@admin_required
def interactions():
    """Customer interactions page"""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    interactions = CustomerInteraction.query.order_by(
        desc(CustomerInteraction.created_at)
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("crm/interactions.html", interactions=interactions)


def calculate_growth_rate(model, field, start_date, **filters):
    """Calculate growth rate for a model"""
    try:
        current_count = model.query.filter_by(**filters).count()
        previous_count = (
            model.query.filter(getattr(model, "created_at") < start_date)
            .filter_by(**filters)
            .count()
        )

        if previous_count == 0:
            return 100 if current_count > 0 else 0

        return round(((current_count - previous_count) / previous_count * 100), 2)
    except:
        return 0
