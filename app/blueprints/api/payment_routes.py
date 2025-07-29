# api/payment.py

from flask import request, jsonify, current_app, url_for
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

# Import the api blueprint from the current module
from . import api_bp


@api_bp.route("/process-payment", methods=["POST"])
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
                payment_method="paypal",
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


@api_bp.route("/subscription-status", methods=["GET"])
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


@api_bp.route("/cancel-subscription", methods=["POST"])
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


@api_bp.route("/create-stripe-session", methods=["POST"])
@login_required
def create_stripe_session():
    """Create Stripe checkout session for payment"""
    try:
        # Validate CSRF
        csrf_token = request.headers.get("X-CSRFToken")
        validate_csrf(csrf_token)

        # Check if Stripe is configured
        if not current_app.config.get("STRIPE_SECRET_KEY"):
            return jsonify({"success": False, "error": "Stripe not configured"}), 400

        import stripe

        stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY")

        data = request.get_json()
        plan_type = data.get("planType")
        currency = data.get("currency", "usd")
        amount = data.get("amount")

        if not all([plan_type, amount]):
            return jsonify({"success": False, "error": "Missing required data"}), 400

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": "Super SEO Toolkit Pro Subscription",
                            "description": "Unlock unlimited AI writing tools and premium features",
                        },
                        "unit_amount": int(amount),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=url_for("main.pricing", _external=True)
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("main.pricing", _external=True),
            client_reference_id=str(current_user.id),
            metadata={
                "user_id": current_user.id,
                "plan_type": plan_type,
                "currency": currency,
                "amount": str(amount),
            },
        )

        return jsonify({"success": True, "sessionId": session.id})

    except Exception as e:
        current_app.logger.error(f"Stripe session creation error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to create payment session"}),
            500,
        )


@api_bp.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        import stripe

        stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY")

        endpoint_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")
        if not endpoint_secret:
            current_app.logger.error("Stripe webhook secret not configured")
            return jsonify({"error": "Webhook secret not configured"}), 400

        payload = request.get_data()
        sig_header = request.headers.get("Stripe-Signature")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            current_app.logger.error(f"Invalid payload: {e}")
            return jsonify({"error": "Invalid payload"}), 400
        except stripe.error.SignatureVerificationError as e:
            current_app.logger.error(f"Invalid signature: {e}")
            return jsonify({"error": "Invalid signature"}), 400

        # Handle the checkout.session.completed event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            # Get user info from metadata
            user_id = session.get("client_reference_id")
            metadata = session.get("metadata", {})

            if not user_id:
                current_app.logger.error("No user ID in Stripe session")
                return jsonify({"error": "No user ID"}), 400

            from app.models.user import User

            user = User.query.get(int(user_id))
            if not user:
                current_app.logger.error(f"User not found: {user_id}")
                return jsonify({"error": "User not found"}), 400

            # Get or create user subscription
            subscription = user.subscription
            if not subscription:
                subscription = Subscription(
                    user_id=user.id,
                    subscription_type=SubscriptionType.FREE,
                    status=SubscriptionStatus.ACTIVE,
                )
                db.session.add(subscription)
                db.session.flush()

            # Upgrade to Pro
            plan_type = metadata.get("plan_type")
            if plan_type == "pro":
                subscription.upgrade_to_pro()

                # Record payment
                payment = Payment(
                    subscription_id=subscription.id,
                    stripe_payment_intent_id=session.get("payment_intent"),
                    stripe_session_id=session.get("id"),
                    amount=str(
                        session.get("amount_total", 0) / 100
                    ),  # Convert from cents
                    currency=session.get("currency", "usd"),
                    status="completed",
                    payment_method="stripe",
                )
                db.session.add(payment)

                # Update user premium status for backward compatibility
                user.is_premium = True
                db.session.commit()

                current_app.logger.info(f"Stripe payment completed for user {user_id}")

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Stripe webhook error: {str(e)}")
        return jsonify({"error": "Webhook processing failed"}), 500
