from functools import wraps
from flask import request, jsonify, session
from flask_login import current_user
from datetime import datetime, timedelta
from utils.extensions import db
from models.crm import UserBehavior, BusinessMetrics, Lead, CustomerInteraction
from models.subscription import UsageTracking
import json
import uuid


def track_page_view(page_name=None):
    """Decorator to track page views and user behavior"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Generate or get session ID
                if "session_id" not in session:
                    session["session_id"] = str(uuid.uuid4())

                # Track page view
                if current_user.is_authenticated:
                    user_id = current_user.id
                else:
                    user_id = None

                behavior = UserBehavior(
                    user_id=user_id,
                    session_id=session["session_id"],
                    page_url=request.url,
                    action="page_view",
                    tool_name=page_name,
                    device_type=get_device_type(request.user_agent.string),
                    browser=request.user_agent.browser,
                    ip_address=request.remote_addr,
                    referrer=request.referrer,
                )

                db.session.add(behavior)
                db.session.commit()

                # Update business metrics
                update_daily_metrics()

            except Exception as e:
                print(f"Error tracking page view: {e}")

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def track_user_engagement(action, tool_name=None, time_spent=None):
    """Track specific user actions and engagement"""
    try:
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())

        behavior = UserBehavior(
            user_id=current_user.id if current_user.is_authenticated else None,
            session_id=session["session_id"],
            page_url=request.url,
            action=action,
            tool_name=tool_name,
            time_spent=time_spent,
            device_type=get_device_type(request.user_agent.string),
            browser=request.user_agent.browser,
            ip_address=request.remote_addr,
            referrer=request.referrer,
        )

        db.session.add(behavior)
        db.session.commit()

    except Exception as e:
        print(f"Error tracking engagement: {e}")


def create_lead_from_contact(
    email, name=None, phone=None, message=None, source="contact_form"
):
    """Create a lead from contact form submission"""
    try:
        # Check if lead already exists
        existing_lead = Lead.query.filter_by(email=email).first()

        if existing_lead:
            # Update existing lead
            existing_lead.last_contact = datetime.utcnow()
            if name:
                existing_lead.name = name
            if phone:
                existing_lead.phone = phone
            if message:
                existing_lead.notes = (
                    existing_lead.notes or ""
                ) + f"\n{datetime.utcnow()}: {message}"
        else:
            # Create new lead
            lead = Lead(
                email=email,
                name=name,
                phone=phone,
                source=source,
                status="new",
                interest_level=2,  # Medium interest from contact form
                notes=message,
                last_contact=datetime.utcnow(),
                next_followup=datetime.utcnow() + timedelta(days=1),
            )
            db.session.add(lead)

        db.session.commit()
        return True

    except Exception as e:
        print(f"Error creating lead: {e}")
        return False


def track_tool_conversion(user_id, tool_name, converted_to_subscriber=False):
    """Track tool usage to subscription conversion"""
    try:
        if converted_to_subscriber:
            # Record conversion event
            behavior = UserBehavior(
                user_id=user_id,
                session_id=session.get("session_id", str(uuid.uuid4())),
                page_url=request.url,
                action="subscription_conversion",
                tool_name=tool_name,
                device_type=get_device_type(request.user_agent.string),
                browser=request.user_agent.browser,
                ip_address=request.remote_addr,
            )
            db.session.add(behavior)

            # Update lead status if exists
            user = db.session.get(User, user_id)
            if user:
                lead = Lead.query.filter_by(email=user.email).first()
                if lead:
                    lead.status = "converted"
                    lead.converted_user_id = user_id

            db.session.commit()

    except Exception as e:
        print(f"Error tracking conversion: {e}")


def get_customer_journey(user_id):
    """Get complete customer journey for a user"""
    try:
        # Get user behavior
        behaviors = (
            UserBehavior.query.filter_by(user_id=user_id)
            .order_by(UserBehavior.created_at)
            .all()
        )

        # Get tool usage
        usage = (
            UsageTracking.query.filter_by(user_id=user_id)
            .order_by(UsageTracking.created_at)
            .all()
        )

        # Get interactions
        interactions = (
            CustomerInteraction.query.filter_by(user_id=user_id)
            .order_by(CustomerInteraction.created_at)
            .all()
        )

        journey = []

        # Combine all touchpoints
        for behavior in behaviors:
            journey.append(
                {
                    "timestamp": behavior.created_at,
                    "type": "behavior",
                    "action": behavior.action,
                    "details": behavior.tool_name or behavior.page_url,
                    "source": behavior.referrer,
                }
            )

        for usage in usage:
            journey.append(
                {
                    "timestamp": usage.created_at,
                    "type": "tool_usage",
                    "action": "used_tool",
                    "details": usage.tool_name,
                    "count": usage.usage_count,
                }
            )

        for interaction in interactions:
            journey.append(
                {
                    "timestamp": interaction.created_at,
                    "type": "interaction",
                    "action": interaction.interaction_type,
                    "details": interaction.subject,
                    "status": interaction.status,
                }
            )

        # Sort by timestamp
        journey.sort(key=lambda x: x["timestamp"])

        return journey

    except Exception as e:
        print(f"Error getting customer journey: {e}")
        return []


def update_daily_metrics():
    """Update daily business metrics"""
    try:
        today = datetime.utcnow().date()

        # Page views
        daily_page_views = UserBehavior.query.filter(
            db.func.date(UserBehavior.created_at) == today,
            UserBehavior.action == "page_view",
        ).count()

        BusinessMetrics.record_metric(
            "daily_page_views", daily_page_views, "traffic", today
        )

        # Tool usage
        daily_tool_usage = UsageTracking.query.filter(
            UsageTracking.usage_date == today
        ).count()

        BusinessMetrics.record_metric(
            "daily_tool_usage", daily_tool_usage, "tools", today
        )

        # New leads
        daily_leads = Lead.query.filter(db.func.date(Lead.created_at) == today).count()

        BusinessMetrics.record_metric("daily_leads", daily_leads, "leads", today)

    except Exception as e:
        print(f"Error updating metrics: {e}")


def get_device_type(user_agent_string):
    """Determine device type from user agent"""
    user_agent_string = user_agent_string.lower()

    if (
        "mobile" in user_agent_string
        or "android" in user_agent_string
        or "iphone" in user_agent_string
    ):
        return "mobile"
    elif "tablet" in user_agent_string or "ipad" in user_agent_string:
        return "tablet"
    else:
        return "desktop"


def get_conversion_funnel_data(days=30):
    """Get conversion funnel data for analytics"""
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        # Visitors (unique sessions)
        visitors = (
            db.session.query(db.func.count(db.func.distinct(UserBehavior.session_id)))
            .filter(
                db.func.date(UserBehavior.created_at) >= start_date,
                UserBehavior.action == "page_view",
            )
            .scalar()
            or 0
        )

        # Tool users (users who used at least one tool)
        tool_users = (
            db.session.query(db.func.count(db.func.distinct(UsageTracking.user_id)))
            .filter(UsageTracking.usage_date >= start_date)
            .scalar()
            or 0
        )

        # Leads generated
        leads = Lead.query.filter(db.func.date(Lead.created_at) >= start_date).count()

        # Conversions (new subscribers)
        from models.subscription import UserSubscription

        conversions = UserSubscription.query.filter(
            db.func.date(UserSubscription.created_at) >= start_date,
            UserSubscription.status == "active",
        ).count()

        return {
            "visitors": visitors,
            "tool_users": tool_users,
            "leads": leads,
            "conversions": conversions,
            "visitor_to_user_rate": round(
                (tool_users / visitors * 100) if visitors > 0 else 0, 2
            ),
            "user_to_lead_rate": round(
                (leads / tool_users * 100) if tool_users > 0 else 0, 2
            ),
            "lead_to_conversion_rate": round(
                (conversions / leads * 100) if leads > 0 else 0, 2
            ),
            "overall_conversion_rate": round(
                (conversions / visitors * 100) if visitors > 0 else 0, 2
            ),
        }

    except Exception as e:
        print(f"Error getting funnel data: {e}")
        return {
            "visitors": 0,
            "tool_users": 0,
            "leads": 0,
            "conversions": 0,
            "visitor_to_user_rate": 0,
            "user_to_lead_rate": 0,
            "lead_to_conversion_rate": 0,
            "overall_conversion_rate": 0,
        }


class CRMInsights:
    """Advanced CRM insights and recommendations"""

    @staticmethod
    def get_user_risk_score(user_id):
        """Calculate churn risk score for a user (0-100)"""
        try:
            from models.subscription import UserSubscription
            from users.models.user import User

            user = User.query.get(user_id)
            if not user:
                return 0

            score = 0

            # Check subscription status
            subscription = UserSubscription.query.filter_by(
                user_id=user_id, status="active"
            ).first()

            if not subscription:
                score += 30  # No active subscription = higher risk

            # Check recent activity
            recent_activity = UserBehavior.query.filter(
                UserBehavior.user_id == user_id,
                UserBehavior.created_at >= datetime.utcnow() - timedelta(days=30),
            ).count()

            if recent_activity == 0:
                score += 40  # No recent activity = high risk
            elif recent_activity < 5:
                score += 20  # Low activity = medium risk

            # Check tool usage
            recent_usage = UsageTracking.query.filter(
                UsageTracking.user_id == user_id,
                UsageTracking.usage_date
                >= datetime.utcnow().date() - timedelta(days=30),
            ).count()

            if recent_usage == 0:
                score += 30  # No tool usage = high risk

            return min(score, 100)

        except Exception as e:
            print(f"Error calculating risk score: {e}")
            return 0

    @staticmethod
    def get_user_recommendations(user_id):
        """Get personalized recommendations for a user"""
        try:
            recommendations = []

            # Get user's tool usage patterns
            top_tools = (
                db.session.query(
                    UsageTracking.tool_name,
                    db.func.sum(UsageTracking.usage_count).label("usage"),
                )
                .filter(UsageTracking.user_id == user_id)
                .group_by(UsageTracking.tool_name)
                .order_by(db.desc("usage"))
                .limit(3)
                .all()
            )

            # Recommend complementary tools
            tool_recommendations = {
                "seo-analyzer": ["keyword-research", "backlink-checker"],
                "keyword-research": ["content-optimizer", "serp-analyzer"],
                "backlink-checker": ["competitor-analysis", "link-builder"],
            }

            used_tools = [tool.tool_name for tool in top_tools]

            for tool in used_tools:
                if tool in tool_recommendations:
                    for rec_tool in tool_recommendations[tool]:
                        if rec_tool not in used_tools:
                            recommendations.append(
                                {
                                    "type": "tool",
                                    "title": f'Try {rec_tool.replace("-", " ").title()}',
                                    "description": f'Since you use {tool.replace("-", " ")}, you might like this complementary tool.',
                                    "action_url": f"/tools/{rec_tool}",
                                    "priority": "medium",
                                }
                            )

            # Check if user should upgrade
            from models.subscription import UserSubscription

            subscription = UserSubscription.query.filter_by(
                user_id=user_id, status="active"
            ).first()

            if not subscription:
                daily_usage = UsageTracking.get_daily_usage(user_id)
                if daily_usage >= 8:  # Close to free limit
                    recommendations.append(
                        {
                            "type": "upgrade",
                            "title": "Upgrade to Pro",
                            "description": "You're using tools frequently. Upgrade for unlimited access.",
                            "action_url": "/subscription/plans",
                            "priority": "high",
                        }
                    )

            return recommendations[:5]  # Return top 5 recommendations

        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
