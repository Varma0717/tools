from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from models.tool_usage import ToolUsage, ToolAnalytics, Subscription
from utils.extensions import db

business_bp = Blueprint("business", __name__, url_prefix="/business")


@business_bp.route("/dashboard")
@login_required
def business_dashboard():
    """Comprehensive business analytics dashboard"""

    # Date ranges
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Revenue Metrics
    active_subscriptions = Subscription.query.filter_by(status="active").count()
    pro_subs = Subscription.query.filter_by(status="active", plan_type="pro").count()
    premium_subs = Subscription.query.filter_by(
        status="active", plan_type="premium"
    ).count()
    enterprise_subs = Subscription.query.filter_by(
        status="active", plan_type="enterprise"
    ).count()

    # Calculate Monthly Recurring Revenue (MRR)
    mrr = (pro_subs * 9.99) + (premium_subs * 19.99) + (enterprise_subs * 49.99)

    # Usage Analytics
    total_usage_today = ToolUsage.query.filter_by(usage_date=today).count()
    total_usage_week = ToolUsage.query.filter(ToolUsage.usage_date >= week_ago).count()
    total_usage_month = ToolUsage.query.filter(
        ToolUsage.usage_date >= month_ago
    ).count()

    # User Segmentation
    anonymous_usage = (
        ToolUsage.query.filter_by(user_id=None)
        .filter(ToolUsage.usage_date >= month_ago)
        .count()
    )
    registered_usage = (
        ToolUsage.query.filter(ToolUsage.user_id.isnot(None))
        .filter(ToolUsage.usage_date >= month_ago)
        .count()
    )
    premium_usage = (
        ToolUsage.query.filter_by(is_premium=True)
        .filter(ToolUsage.usage_date >= month_ago)
        .count()
    )

    # Conversion Metrics
    from users.models import User

    total_users = User.query.count()
    conversion_rate = (
        (active_subscriptions / total_users * 100) if total_users > 0 else 0
    )

    # Tool Popularity (Top 10)
    popular_tools = (
        db.session.query(
            ToolAnalytics.tool_name,
            func.sum(ToolAnalytics.total_uses).label("total_uses"),
        )
        .filter(ToolAnalytics.date >= month_ago)
        .group_by(ToolAnalytics.tool_name)
        .order_by(desc("total_uses"))
        .limit(10)
        .all()
    )

    # Limit Blocks (Monetization Opportunities)
    limit_blocks_today = (
        db.session.query(func.sum(ToolAnalytics.limit_blocks))
        .filter(ToolAnalytics.date == today)
        .scalar()
        or 0
    )

    limit_blocks_month = (
        db.session.query(func.sum(ToolAnalytics.limit_blocks))
        .filter(ToolAnalytics.date >= month_ago)
        .scalar()
        or 0
    )

    # Daily Usage Trend (Last 30 days)
    daily_usage = (
        db.session.query(
            ToolAnalytics.date,
            func.sum(ToolAnalytics.total_uses).label("uses"),
            func.sum(ToolAnalytics.limit_blocks).label("blocks"),
        )
        .filter(ToolAnalytics.date >= month_ago)
        .group_by(ToolAnalytics.date)
        .order_by(ToolAnalytics.date)
        .all()
    )

    # Projected Metrics
    avg_daily_blocks = limit_blocks_month / 30 if limit_blocks_month > 0 else 0
    potential_conversions = avg_daily_blocks * 0.05  # 5% conversion rate assumption
    projected_monthly_revenue = (
        potential_conversions * 30 * 19.99
    )  # Assume Premium plan

    # Competitive Analysis Data
    competitive_data = {
        "seoptimer_tools": 18,
        "our_tools": 168,
        "seoptimer_price": 29,
        "our_price": 19.99,
        "tool_advantage": round((168 / 18) * 100, 1),
        "price_advantage": round(((29 - 19.99) / 29) * 100, 1),
    }

    return render_template(
        "business/dashboard.html",
        # Revenue
        mrr=mrr,
        active_subscriptions=active_subscriptions,
        pro_subs=pro_subs,
        premium_subs=premium_subs,
        enterprise_subs=enterprise_subs,
        # Usage
        total_usage_today=total_usage_today,
        total_usage_week=total_usage_week,
        total_usage_month=total_usage_month,
        # Segmentation
        anonymous_usage=anonymous_usage,
        registered_usage=registered_usage,
        premium_usage=premium_usage,
        # Conversion
        total_users=total_users,
        conversion_rate=conversion_rate,
        # Analytics
        popular_tools=popular_tools,
        limit_blocks_today=limit_blocks_today,
        limit_blocks_month=limit_blocks_month,
        daily_usage=daily_usage,
        # Projections
        potential_conversions=potential_conversions,
        projected_monthly_revenue=projected_monthly_revenue,
        # Competitive
        competitive_data=competitive_data,
    )


@business_bp.route("/api/revenue-forecast")
@login_required
def revenue_forecast():
    """API endpoint for revenue forecasting"""

    # Current metrics
    active_subs = Subscription.query.filter_by(status="active").count()
    month_ago = datetime.utcnow().date() - timedelta(days=30)
    monthly_blocks = (
        db.session.query(func.sum(ToolAnalytics.limit_blocks))
        .filter(ToolAnalytics.date >= month_ago)
        .scalar()
        or 0
    )

    # Forecasting scenarios
    scenarios = {
        "conservative": {
            "conversion_rate": 0.02,  # 2%
            "avg_plan_price": 9.99,
            "growth_rate": 1.1,  # 10% monthly growth
        },
        "realistic": {
            "conversion_rate": 0.05,  # 5%
            "avg_plan_price": 14.99,  # Mix of Pro and Premium
            "growth_rate": 1.2,  # 20% monthly growth
        },
        "optimistic": {
            "conversion_rate": 0.1,  # 10%
            "avg_plan_price": 19.99,
            "growth_rate": 1.3,  # 30% monthly growth
        },
    }

    forecasts = {}

    for scenario, params in scenarios.items():
        monthly_forecast = []
        current_blocks = monthly_blocks
        current_revenue = active_subs * params["avg_plan_price"]

        for month in range(1, 13):  # 12 months
            # Projected new conversions
            new_conversions = current_blocks * params["conversion_rate"]
            new_revenue = new_conversions * params["avg_plan_price"]
            current_revenue += new_revenue

            # Apply growth
            current_blocks *= params["growth_rate"]

            monthly_forecast.append(
                {
                    "month": month,
                    "revenue": round(current_revenue, 2),
                    "new_conversions": round(new_conversions, 0),
                    "total_subscribers": active_subs + (new_conversions * month),
                }
            )

        forecasts[scenario] = monthly_forecast

    return jsonify(forecasts)


@business_bp.route("/api/competitive-analysis")
@login_required
def competitive_analysis():
    """API endpoint for competitive analysis data"""

    competitors = {
        "seoptimer": {
            "name": "SEOptimer",
            "tools": 18,
            "price_basic": 19,
            "price_premium": 49,
            "features": ["SEO Audit", "Keyword Tracking", "Site Monitoring"],
            "limitations": [
                "Limited tools",
                "No content generation",
                "No technical utilities",
            ],
        },
        "semrush": {
            "name": "SEMrush",
            "tools": 40,
            "price_basic": 99,
            "price_premium": 199,
            "features": ["Comprehensive SEO", "PPC Tools", "Content Marketing"],
            "limitations": [
                "Very expensive",
                "Complex interface",
                "Overkill for small businesses",
            ],
        },
        "ahrefs": {
            "name": "Ahrefs",
            "tools": 35,
            "price_basic": 99,
            "price_premium": 179,
            "features": ["Backlink Analysis", "Keyword Research", "Site Explorer"],
            "limitations": [
                "Expensive",
                "Limited content tools",
                "No technical utilities",
            ],
        },
    }

    our_advantage = {
        "name": "Super SEO Toolkit",
        "tools": 168,
        "price_basic": 9.99,
        "price_premium": 19.99,
        "features": [
            "168+ Tools (9x more than competitors)",
            "SEO + Content + Technical + Security",
            "All-in-one platform",
            "Affordable pricing",
            "No complex learning curve",
            "Perfect for small-medium businesses",
        ],
        "advantages": [
            "80% cost savings vs competitors",
            "4-9x more tools than any competitor",
            "Integrated dashboard",
            "Simple pricing model",
            "No feature limitations",
        ],
    }

    return jsonify({"competitors": competitors, "our_advantage": our_advantage})


@business_bp.route("/strategy")
@login_required
def business_strategy():
    """Display comprehensive business strategy"""
    return render_template("business/strategy.html")
