from app.core.extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    role = db.Column(db.String(10), default="customer")
    is_premium = db.Column(db.Boolean, default=False)
    package_type = db.Column(db.String(20), default="free")  # free, pro
    subscription_active = db.Column(db.Boolean, default=False)
    trial_used = db.Column(db.Boolean, default=False)
    daily_tool_usage = db.Column(db.Integer, default=0)
    last_usage_reset = db.Column(db.Date, default=db.func.current_date())

    # Profile fields
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

    # Relationships (if tables exist)
    orders = db.relationship("Order", back_populates="user", lazy=True)
    downloads = db.relationship("Download", back_populates="user", lazy=True)
    subscription = relationship("Subscription", back_populates="user", uselist=False)

    def is_admin(self):
        return self.role == "admin"

    def is_customer(self):
        return self.role == "customer"

    def has_pro_subscription(self):
        """Check if user has active pro subscription"""
        return self.package_type == "pro" and self.subscription_active

    def is_free_user(self):
        """Check if user is on free plan"""
        return self.package_type == "free"

    def is_pro_user(self):
        """Check if user is on pro plan"""
        return self.package_type == "pro" and self.subscription_active

    def can_use_tool(self, tool_type="free"):
        """Check if user can use a specific tool type"""
        if self.is_pro_user():
            return True

        if tool_type == "free":
            # Free users have unlimited access to free tools
            return True

        return False

    def get_package_display_name(self):
        """Get user-friendly package name"""
        if self.is_pro_user():
            return "Pro"
        return "Free"

    def get_tool_usage_limit(self):
        """Get daily tool usage limit based on package"""
        if self.is_pro_user():
            return float("inf")  # Unlimited
        return 100  # Free users get 100 daily uses

    def get_ai_tool_usage_this_month(self):
        """Get AI tool usage count for current month"""
        from app.models.subscription import AIToolUsage

        return AIToolUsage.get_monthly_usage(self.id)
