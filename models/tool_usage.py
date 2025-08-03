from utils.extensions import db
from datetime import datetime, timedelta
from flask_login import current_user


class ToolUsage(db.Model):
    """Track tool usage for monetization"""

    __tablename__ = "tool_usage"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True
    )  # None for anonymous
    ip_address = db.Column(db.String(45), nullable=False)  # Support IPv6
    tool_name = db.Column(db.String(100), nullable=False)
    tool_category = db.Column(db.String(50), nullable=False)
    usage_date = db.Column(db.Date, default=datetime.utcnow().date)
    usage_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ToolUsage {self.tool_name} by {self.user_id or self.ip_address}>"

    @staticmethod
    def get_daily_usage(user_id=None, ip_address=None):
        """Get today's usage count for user or IP"""
        today = datetime.utcnow().date()
        query = ToolUsage.query.filter_by(usage_date=today)

        if user_id:
            query = query.filter_by(user_id=user_id)
        else:
            query = query.filter_by(ip_address=ip_address, user_id=None)

        return query.count()

    @staticmethod
    def get_monthly_usage(user_id):
        """Get current month's usage count for registered user"""
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)

        return ToolUsage.query.filter(
            ToolUsage.user_id == user_id, ToolUsage.usage_date >= month_start
        ).count()

    @staticmethod
    def can_use_tool(user_id=None, ip_address=None, user_subscription=None):
        """Check if user can use tools based on limits"""
        if user_subscription == "premium":
            return True, "unlimited"

        if user_id:
            monthly_usage = ToolUsage.get_monthly_usage(user_id)
            if monthly_usage >= 5:
                return False, "monthly_limit_reached"
            return True, f"monthly_remaining_{5 - monthly_usage}"
        else:
            daily_usage = ToolUsage.get_daily_usage(ip_address=ip_address)
            if daily_usage >= 1:
                return False, "daily_limit_reached"
            return True, "daily_remaining"

    @staticmethod
    def record_usage(
        tool_name, tool_category, user_id=None, ip_address=None, is_premium=False
    ):
        """Record tool usage"""
        usage = ToolUsage(
            user_id=user_id,
            ip_address=ip_address,
            tool_name=tool_name,
            tool_category=tool_category,
            is_premium=is_premium,
        )
        db.session.add(usage)
        db.session.commit()
        return usage


class Subscription(db.Model):
    """User subscription management"""

    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)  # 'premium', 'enterprise'
    status = db.Column(
        db.String(20), default="active"
    )  # 'active', 'canceled', 'expired'
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Subscription {self.plan_type} for user {self.user_id}>"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == "active" and self.end_date > datetime.utcnow()

    @staticmethod
    def get_user_subscription(user_id):
        """Get active subscription for user"""
        return (
            Subscription.query.filter_by(user_id=user_id, status="active")
            .filter(Subscription.end_date > datetime.utcnow())
            .first()
        )


class ToolAnalytics(db.Model):
    """Analytics for tool usage and business insights"""

    __tablename__ = "tool_analytics"

    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    total_uses = db.Column(db.Integer, default=0)
    anonymous_uses = db.Column(db.Integer, default=0)
    registered_uses = db.Column(db.Integer, default=0)
    premium_uses = db.Column(db.Integer, default=0)
    limit_blocks = db.Column(db.Integer, default=0)  # How many times users hit limits

    @staticmethod
    def update_stats(tool_name, is_anonymous=True, is_premium=False, was_blocked=False):
        """Update daily analytics for a tool"""
        today = datetime.utcnow().date()
        stats = ToolAnalytics.query.filter_by(tool_name=tool_name, date=today).first()

        if not stats:
            stats = ToolAnalytics(tool_name=tool_name, date=today)
            db.session.add(stats)

        # Ensure fields are not None before incrementing
        if stats.total_uses is None:
            stats.total_uses = 0
        if stats.anonymous_uses is None:
            stats.anonymous_uses = 0
        if stats.registered_uses is None:
            stats.registered_uses = 0
        if stats.premium_uses is None:
            stats.premium_uses = 0
        if stats.limit_blocks is None:
            stats.limit_blocks = 0

        stats.total_uses += 1
        if is_anonymous:
            stats.anonymous_uses += 1
        else:
            stats.registered_uses += 1

        if is_premium:
            stats.premium_uses += 1

        if was_blocked:
            stats.limit_blocks += 1

        db.session.commit()
        return stats
