"""
Razorpay Payment Handler for Super SEO Toolkit
Works with existing payment/subscription tables
"""

from app.core.extensions import db
from app.models.subscription import Subscription, SubscriptionType, SubscriptionStatus
from datetime import datetime, timedelta
import json


class RazorpayPaymentHandler:
    """Handle Razorpay payments and update existing subscription system"""

    @staticmethod
    def create_payment_record(
        user_id, razorpay_payment_id, razorpay_order_id, amount, plan, billing_cycle
    ):
        """Create payment record in existing payments table"""
        try:
            # Use existing Payment model structure
            from app.models.order import Payment  # Using existing payment model

            payment = Payment(
                subscription_id=None,  # Will be set after subscription creation
                paypal_payment_id=razorpay_payment_id,  # Reuse this field for Razorpay
                paypal_order_id=razorpay_order_id,  # Reuse this field for Razorpay
                amount=amount,
                currency="USD",
                status="completed",
                payment_method="razorpay",
                created_at=datetime.utcnow(),
            )

            db.session.add(payment)
            db.session.flush()  # Get payment ID

            return payment

        except Exception as e:
            print(f"Error creating payment record: {e}")
            return None

    @staticmethod
    def update_user_subscription(user_id, plan, billing_cycle, payment_id=None):
        """Update user subscription using existing subscription model"""
        try:
            # Get existing subscription or create new one
            subscription = Subscription.query.filter_by(user_id=user_id).first()

            # Map plan names to existing enum
            subscription_type = (
                SubscriptionType.PRO
                if plan == "professional"
                else SubscriptionType.FREE
            )

            # Calculate end date
            if billing_cycle == "annual":
                end_date = datetime.utcnow() + timedelta(days=365)
            else:
                end_date = datetime.utcnow() + timedelta(days=30)

            if subscription:
                # Update existing subscription
                subscription.subscription_type = subscription_type
                subscription.status = SubscriptionStatus.ACTIVE
                subscription.start_date = datetime.utcnow()
                subscription.end_date = end_date
                subscription.updated_at = datetime.utcnow()
            else:
                # Create new subscription
                subscription = Subscription(
                    user_id=user_id,
                    subscription_type=subscription_type,
                    status=SubscriptionStatus.ACTIVE,
                    start_date=datetime.utcnow(),
                    end_date=end_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.session.add(subscription)

            db.session.commit()

            # Update payment record with subscription ID
            if payment_id:
                from app.models.order import Payment

                payment = Payment.query.get(payment_id)
                if payment:
                    payment.subscription_id = subscription.id
                    db.session.commit()

            return subscription

        except Exception as e:
            print(f"Error updating subscription: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def get_user_subscription_info(user_id):
        """Get user's current subscription information"""
        try:
            subscription = Subscription.query.filter_by(user_id=user_id).first()

            if not subscription:
                return {
                    "plan": "free",
                    "status": "active",
                    "is_active": True,
                    "days_remaining": 0,
                    "limits": RazorpayPaymentHandler.get_plan_limits("free"),
                }

            # Check if subscription is still active
            is_active = (
                subscription.status == SubscriptionStatus.ACTIVE
                and subscription.end_date > datetime.utcnow()
            )

            days_remaining = 0
            if subscription.end_date:
                delta = subscription.end_date - datetime.utcnow()
                days_remaining = max(0, delta.days)

            plan_name = (
                "professional"
                if subscription.subscription_type == SubscriptionType.PRO
                else "free"
            )

            return {
                "plan": plan_name,
                "status": subscription.status.value,
                "is_active": is_active,
                "days_remaining": days_remaining,
                "end_date": (
                    subscription.end_date.isoformat() if subscription.end_date else None
                ),
                "limits": RazorpayPaymentHandler.get_plan_limits(plan_name),
            }

        except Exception as e:
            print(f"Error getting subscription info: {e}")
            return {
                "plan": "free",
                "status": "active",
                "is_active": True,
                "days_remaining": 0,
            }

    @staticmethod
    def get_plan_limits(plan):
        """Get usage limits for a plan"""
        limits = {
            "free": {
                "daily_analyses": 5,
                "keywords": 10,
                "competitors": 0,
                "reports_per_month": 5,
                "api_calls_per_day": 0,
            },
            "professional": {
                "daily_analyses": 500,
                "keywords": 100,
                "competitors": 5,
                "reports_per_month": 100,
                "api_calls_per_day": 1000,
            },
        }
        return limits.get(plan, limits["free"])


# Helper function to check if user has active subscription
def user_has_active_subscription(user_id, required_plan="professional"):
    """Check if user has an active subscription for the required plan"""
    subscription_info = RazorpayPaymentHandler.get_user_subscription_info(user_id)

    if required_plan == "free":
        return True  # Everyone has access to free features

    return subscription_info["is_active"] and subscription_info["plan"] == required_plan


# Export the handler
payment_handler = RazorpayPaymentHandler()
