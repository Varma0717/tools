from datetime import datetime, timedelta
from utils.extensions import db
from sqlalchemy import func, desc
import json


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(255))
    source = db.Column(db.String(100))  # website, referral, social, ads, etc.
    status = db.Column(
        db.String(50), default="new"
    )  # new, contacted, qualified, converted, lost
    interest_level = db.Column(db.Integer, default=1)  # 1-5 scale
    estimated_value = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    last_contact = db.Column(db.DateTime)
    next_followup = db.Column(db.DateTime)
    converted_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    assigned_to = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    activities = db.relationship("LeadActivity", backref="lead", lazy="dynamic")
    converted_user = db.relationship(
        "User", foreign_keys=[converted_user_id], backref="converted_from_lead"
    )
    assigned_user = db.relationship(
        "User", foreign_keys=[assigned_to], backref="assigned_leads"
    )


class LeadActivity(db.Model):
    __tablename__ = "lead_activities"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=False)
    activity_type = db.Column(
        db.String(50), nullable=False
    )  # email, call, meeting, demo, quote
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    scheduled_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CustomerInteraction(db.Model):
    __tablename__ = "customer_interactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    interaction_type = db.Column(
        db.String(50), nullable=False
    )  # support, sales, feedback, complaint
    channel = db.Column(db.String(50))  # email, phone, chat, form
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    status = db.Column(
        db.String(50), default="open"
    )  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default="medium")  # low, medium, high, urgent
    assigned_to = db.Column(db.Integer, db.ForeignKey("user.id"))
    resolution = db.Column(db.Text)
    satisfaction_rating = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id], backref="interactions")
    assigned_user = db.relationship(
        "User", foreign_keys=[assigned_to], backref="assigned_interactions"
    )


class CampaignTracking(db.Model):
    __tablename__ = "campaign_tracking"

    id = db.Column(db.Integer, primary_key=True)
    campaign_name = db.Column(db.String(255), nullable=False)
    campaign_type = db.Column(db.String(50))  # email, social, ads, content
    source = db.Column(db.String(100))  # utm_source
    medium = db.Column(db.String(100))  # utm_medium
    campaign = db.Column(db.String(100))  # utm_campaign
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"))
    conversion_value = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserBehavior(db.Model):
    __tablename__ = "user_behavior"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    session_id = db.Column(db.String(255))
    page_url = db.Column(db.String(500))
    action = db.Column(db.String(100))  # page_view, tool_use, download, signup, etc.
    tool_name = db.Column(db.String(100))
    time_spent = db.Column(db.Integer)  # seconds
    device_type = db.Column(db.String(50))
    browser = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    referrer = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BusinessMetrics(db.Model):
    __tablename__ = "business_metrics"

    id = db.Column(db.Integer, primary_key=True)
    metric_date = db.Column(db.Date, nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_category = db.Column(db.String(50))  # revenue, users, tools, conversion
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def record_metric(metric_name, value, category="general", date=None):
        """Record a business metric"""
        if date is None:
            date = datetime.utcnow().date()

        existing = BusinessMetrics.query.filter_by(
            metric_date=date, metric_name=metric_name
        ).first()

        if existing:
            existing.metric_value = value
        else:
            metric = BusinessMetrics(
                metric_date=date,
                metric_name=metric_name,
                metric_value=value,
                metric_category=category,
            )
            db.session.add(metric)

        db.session.commit()


class CustomerSegment(db.Model):
    __tablename__ = "customer_segments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.JSON)  # Stored as JSON for flexible criteria
    color = db.Column(db.String(7), default="#6B7280")  # Hex color for UI
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserSegmentMembership(db.Model):
    __tablename__ = "user_segment_membership"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    segment_id = db.Column(
        db.Integer, db.ForeignKey("customer_segments.id"), nullable=False
    )
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="segment_memberships")
    segment = db.relationship("CustomerSegment", backref="user_memberships")


class CRMDashboardWidget(db.Model):
    __tablename__ = "crm_dashboard_widgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)  # chart, metric, table, etc.
    widget_config = db.Column(db.JSON)  # Widget configuration
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=1)
    height = db.Column(db.Integer, default=1)
    is_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# CRM Analytics Functions
class CRMAnalytics:
    @staticmethod
    def get_lead_conversion_rate(days=30):
        """Calculate lead conversion rate over specified days"""
        start_date = datetime.utcnow().date() - timedelta(days=days)

        total_leads = Lead.query.filter(Lead.created_at >= start_date).count()
        converted_leads = Lead.query.filter(
            Lead.created_at >= start_date, Lead.status == "converted"
        ).count()

        return (converted_leads / total_leads * 100) if total_leads > 0 else 0

    @staticmethod
    def get_customer_lifetime_value():
        """Calculate average customer lifetime value"""
        from models.subscription import UserSubscription

        # Get average subscription duration and value
        active_subscriptions = UserSubscription.query.filter_by(status="active").all()
        if not active_subscriptions:
            return 0

        total_value = sum(sub.plan.price for sub in active_subscriptions)
        return total_value / len(active_subscriptions)

    @staticmethod
    def get_churn_rate(days=30):
        """Calculate customer churn rate"""
        from models.subscription import UserSubscription

        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        # Users who were active at start of period
        active_start = UserSubscription.query.filter(
            UserSubscription.start_date <= start_date,
            UserSubscription.status == "active",
        ).count()

        # Users who cancelled during period
        cancelled = UserSubscription.query.filter(
            UserSubscription.cancelled_at >= start_date,
            UserSubscription.cancelled_at <= end_date,
        ).count()

        return (cancelled / active_start * 100) if active_start > 0 else 0

    @staticmethod
    def get_most_valuable_segments():
        """Get customer segments by value"""
        # This would involve complex queries based on segment criteria
        # For now, return basic structure
        return []

    @staticmethod
    def get_tool_usage_trends(days=30):
        """Get tool usage trends"""
        from models.subscription import UsageTracking

        start_date = datetime.utcnow().date() - timedelta(days=days)

        trends = (
            db.session.query(
                UsageTracking.tool_name,
                func.sum(UsageTracking.usage_count).label("total_usage"),
                func.count(func.distinct(UsageTracking.user_id)).label("unique_users"),
            )
            .filter(UsageTracking.usage_date >= start_date)
            .group_by(UsageTracking.tool_name)
            .order_by(desc("total_usage"))
            .limit(10)
            .all()
        )

        return trends
