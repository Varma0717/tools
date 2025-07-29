# api/payment.py

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from app.models.subscription import (
    Subscription,
    Payment,
    SubscriptionType,
    SubscriptionStatus,
)
from app.core.extensions import db
import os

payment_bp = Blueprint("payment", __name__, url_prefix="/api")


@payment_bp.route("/process-payment", methods=["POST"])
@login_required
def process_payment():
    """Process PayPal payment and upgrade user subscription"""
    try:
        # Validate CSRF
        csrf_token = request.headers.get("X-CSRFToken")
        validate_csrf(csrf_token)

        data = request.get_json()
        order_id = data.get("orderID")
        payment_id = data.get("paymentID")
        plan_type = data.get("planType")
        currency = data.get("currency")
        amount = data.get("amount")

        if not all([order_id, payment_id, plan_type, currency, amount]):
            return (
                jsonify({"success": False, "error": "Missing required payment data"}),
                400,
            )

        # Get or create user subscription
        subscription = current_user.subscription
        if not subscription:
            subscription = Subscription(
                user_id=current_user.id,
                subscription_type=SubscriptionType.FREE,
                status=SubscriptionStatus.ACTIVE,
            )
            db.session.add(subscription)
            db.session.flush()  # Get the ID

        # Upgrade to Pro
        if plan_type == "pro":
            subscription.upgrade_to_pro()

            # Record payment
            payment = Payment(
                subscription_id=subscription.id,
                paypal_payment_id=payment_id,
                paypal_order_id=order_id,
                amount=amount,
                currency=currency,
                status="completed",
            )
            db.session.add(payment)

            # Update user premium status for backward compatibility
            current_user.is_premium = True

            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": "Payment processed successfully! Your Pro subscription is now active.",
                    "subscription_type": "pro",
                }
            )

        return jsonify({"success": False, "error": "Invalid plan type"}), 400

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Payment processing error: {str(e)}")
        return jsonify({"success": False, "error": "Payment processing failed"}), 500


@payment_bp.route("/subscription-status", methods=["GET"])
@login_required
def subscription_status():
    """Get current user subscription status"""
    subscription = current_user.subscription

    if not subscription:
        return jsonify(
            {
                "subscription_type": "free",
                "status": "active",
                "ai_usage_this_month": current_user.get_ai_tool_usage_this_month(),
                "ai_usage_limit": 5,
            }
        )

    return jsonify(
        {
            "subscription_type": subscription.subscription_type.value,
            "status": subscription.status.value,
            "is_active": subscription.is_active,
            "is_pro": subscription.is_pro,
            "start_date": (
                subscription.start_date.isoformat() if subscription.start_date else None
            ),
            "end_date": (
                subscription.end_date.isoformat() if subscription.end_date else None
            ),
            "ai_usage_this_month": current_user.get_ai_tool_usage_this_month(),
            "ai_usage_limit": None if subscription.is_pro else 5,
        }
    )


@payment_bp.route("/cancel-subscription", methods=["POST"])
@login_required
def cancel_subscription():
    """Cancel user subscription"""
    try:
        csrf_token = request.headers.get("X-CSRFToken")
        validate_csrf(csrf_token)

        subscription = current_user.subscription
        if not subscription or not subscription.is_pro:
            return (
                jsonify(
                    {"success": False, "error": "No active Pro subscription found"}
                ),
                400,
            )

        subscription.cancel_subscription()
        current_user.is_premium = False

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Subscription cancelled successfully. You will retain Pro access until the end of your billing period.",
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Subscription cancellation error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to cancel subscription"}),
            500,
        )
