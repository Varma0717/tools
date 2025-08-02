from datetime import datetime, timedelta
from utils.extensions import db


class SubscriptionPlan(db.Model):
    __tablename__ = "subscription_plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Free, Pro, Enterprise
    price = db.Column(db.Float, nullable=False, default=0.0)
    billing_cycle = db.Column(
        db.String(20), nullable=False, default="monthly"
    )  # monthly, yearly
    max_daily_usage = db.Column(db.Integer, default=10)  # SEO tool uses per day
    max_reports = db.Column(db.Integer, default=5)  # PDF reports per month
    features = db.Column(db.JSON, default=list)  # List of included features
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subscriptions = db.relationship("UserSubscription", backref="plan", lazy="dynamic")


class UserSubscription(db.Model):
    __tablename__ = "user_subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    plan_id = db.Column(
        db.Integer, db.ForeignKey("subscription_plans.id"), nullable=False
    )

    # Payment details
    stripe_subscription_id = db.Column(db.String(255), unique=True)
    payment_method = db.Column(
        db.String(50), default="stripe"
    )  # stripe, paypal, razorpay
    status = db.Column(
        db.String(20), default="active"
    )  # active, cancelled, expired, pending

    # Dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    trial_end_date = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != "active":
            return False
        if self.end_date and self.end_date < datetime.utcnow():
            return False
        return True

    def days_remaining(self):
        """Get days remaining in subscription"""
        if not self.end_date:
            return None
        remaining = self.end_date - datetime.utcnow()
        return max(0, remaining.days)

    def extend_subscription(self, months=1):
        """Extend subscription by specified months"""
        if not self.end_date:
            self.end_date = datetime.utcnow()
        self.end_date += timedelta(days=30 * months)
        db.session.commit()


class UsageTracking(db.Model):
    __tablename__ = "usage_tracking"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)
    usage_date = db.Column(db.Date, default=datetime.utcnow().date)
    usage_count = db.Column(db.Integer, default=1)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def track_usage(user_id, tool_name, ip_address=None, user_agent=None):
        """Track tool usage for rate limiting and analytics"""
        today = datetime.utcnow().date()
        existing = UsageTracking.query.filter_by(
            user_id=user_id, tool_name=tool_name, usage_date=today
        ).first()

        if existing:
            existing.usage_count += 1
        else:
            usage = UsageTracking(
                user_id=user_id,
                tool_name=tool_name,
                usage_date=today,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.session.add(usage)

        db.session.commit()

    @staticmethod
    def get_daily_usage(user_id, tool_name=None):
        """Get user's daily usage count"""
        today = datetime.utcnow().date()
        query = UsageTracking.query.filter_by(user_id=user_id, usage_date=today)

        if tool_name:
            query = query.filter_by(tool_name=tool_name)
            usage = query.first()
            return usage.usage_count if usage else 0
        else:
            # Return total daily usage across all tools
            result = query.with_entities(
                db.func.sum(UsageTracking.usage_count)
            ).scalar()
            return result or 0


class APIUsage(db.Model):
    __tablename__ = "api_usage"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    api_key_id = db.Column(db.String(100))  # For API key tracking
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), default="POST")

    # Usage details
    usage_date = db.Column(db.Date, default=datetime.utcnow().date)
    usage_count = db.Column(db.Integer, default=1)
    response_time_ms = db.Column(db.Integer)  # Track performance
    status_code = db.Column(db.Integer)

    # Request details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
