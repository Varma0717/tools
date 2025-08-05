from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import stripe
import razorpay
import os
from utils.extensions import db
from models.subscription import SubscriptionPlan, UserSubscription, UsageTracking

subscription_bp = Blueprint("subscription", __name__, url_prefix="/subscription")

# Payment gateway configurations
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Razorpay configuration
razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID", ""), os.getenv("RAZORPAY_KEY_SECRET", ""))
)

# PayPal configuration (you'll need to implement PayPal SDK separately)
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")


@subscription_bp.route("/plans")
def pricing():
    """Display professional subscription plans for developers"""
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    return render_template("subscription/pricing.html", plans=plans)


@subscription_bp.route("/checkout/<int:plan_id>")
@login_required
def checkout(plan_id):
    """Checkout page for a specific plan"""
    plan = SubscriptionPlan.query.get_or_404(plan_id)

    # Check if user already has an active subscription
    existing_subscription = UserSubscription.query.filter_by(
        user_id=current_user.id, status="active"
    ).first()

    if existing_subscription:
        flash(
            "You already have an active subscription. Please cancel it first to switch plans.",
            "warning",
        )
        return redirect(url_for("users.account"))

    return render_template("subscription/checkout.html", plan=plan)


@subscription_bp.route("/create-payment-intent", methods=["POST"])
@login_required
def create_payment_intent():
    """Create Stripe payment intent"""
    try:
        data = request.get_json()
        plan_id = data.get("plan_id")

        plan = SubscriptionPlan.query.get_or_404(plan_id)

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(plan.price * 100),  # Convert to cents
            currency="usd",
            metadata={"user_id": current_user.id, "plan_id": plan_id},
        )

        return jsonify({"success": True, "client_secret": intent.client_secret})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@subscription_bp.route("/confirm-subscription", methods=["POST"])
@login_required
def confirm_subscription():
    """Confirm subscription after successful payment"""
    try:
        data = request.get_json()
        payment_intent_id = data.get("payment_intent_id")
        plan_id = data.get("plan_id")

        # Verify payment with Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status != "succeeded":
            return jsonify({"success": False, "error": "Payment not confirmed"}), 400

        plan = SubscriptionPlan.query.get_or_404(plan_id)

        # Calculate end date based on billing cycle
        start_date = datetime.utcnow()
        if plan.billing_cycle == "monthly":
            end_date = start_date + timedelta(days=30)
        else:  # yearly
            end_date = start_date + timedelta(days=365)

        # Create subscription record
        subscription = UserSubscription(
            user_id=current_user.id,
            plan_id=plan_id,
            stripe_subscription_id=payment_intent_id,
            status="active",
            start_date=start_date,
            end_date=end_date,
        )

        db.session.add(subscription)
        db.session.commit()

        return jsonify(
            {"success": True, "message": "Subscription activated successfully!"}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@subscription_bp.route("/cancel", methods=["POST"])
@login_required
def cancel_subscription():
    """Cancel user's current subscription"""
    try:
        subscription = UserSubscription.query.filter_by(
            user_id=current_user.id, status="active"
        ).first()

        if not subscription:
            return (
                jsonify({"success": False, "error": "No active subscription found"}),
                404,
            )

        # Cancel with Stripe if applicable
        if subscription.stripe_subscription_id:
            try:
                stripe.Subscription.delete(subscription.stripe_subscription_id)
            except:
                pass  # Continue even if Stripe cancellation fails

        # Update subscription status
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()

        db.session.commit()

        flash("Your subscription has been cancelled successfully.", "success")
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@subscription_bp.route("/usage-stats")
@login_required
def usage_stats():
    """Get user's usage statistics"""
    if not current_user.subscription:
        return jsonify({"error": "No active subscription"}), 404

    today = datetime.utcnow().date()

    # Get today's usage
    today_usage = (
        db.session.query(db.func.sum(UsageTracking.usage_count))
        .filter(
            UsageTracking.user_id == current_user.id, UsageTracking.usage_date == today
        )
        .scalar()
        or 0
    )

    # Get this month's usage
    month_start = today.replace(day=1)
    monthly_usage = (
        db.session.query(db.func.sum(UsageTracking.usage_count))
        .filter(
            UsageTracking.user_id == current_user.id,
            UsageTracking.usage_date >= month_start,
        )
        .scalar()
        or 0
    )

    plan = current_user.subscription.plan

    return jsonify(
        {
            "daily_usage": today_usage,
            "daily_limit": plan.max_daily_usage,
            "monthly_usage": monthly_usage,
            "monthly_limit": plan.max_reports,
            "plan_name": plan.name,
        }
    )


@subscription_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        # Handle successful payment

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        # Handle failed payment

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        # Handle subscription cancellation

    return jsonify({"status": "success"})
