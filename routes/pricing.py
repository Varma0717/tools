from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from flask_login import login_required, current_user
import stripe
import os
from datetime import datetime, timedelta
from models.tool_usage import Subscription
from utils.extensions import db

pricing_bp = Blueprint("pricing", __name__)

# Stripe configuration
stripe.api_key = os.environ.get(
    "STRIPE_SECRET_KEY", "sk_test_..."
)  # Replace with actual key

PRICING_PLANS = {
    "pro": {
        "name": "Pro Plan",
        "price": 9.99,
        "monthly_tools": 50,
        "features": [
            "50 tool uses per month",
            "Priority email support",
            "Usage analytics",
            "Export reports (CSV)",
            "Ad-free experience",
        ],
        "stripe_price_id": "price_pro_monthly",  # Replace with actual Stripe price ID
    },
    "premium": {
        "name": "Premium Plan",
        "price": 19.99,
        "monthly_tools": "unlimited",
        "features": [
            "Unlimited tool usage",
            "Priority support + live chat",
            "Advanced analytics",
            "Export reports (PDF/CSV)",
            "Ad-free experience",
            "API access (1000 calls/month)",
            "Bulk URL analysis",
            "Custom branding",
        ],
        "stripe_price_id": "price_premium_monthly",  # Replace with actual Stripe price ID
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "price": 49.99,
        "monthly_tools": "unlimited",
        "features": [
            "Everything in Premium",
            "White-label solution",
            "Unlimited API access",
            "Custom integrations",
            "Dedicated account manager",
            "Team collaboration (up to 10 users)",
            "Advanced reporting",
            "SLA guarantee",
        ],
        "stripe_price_id": "price_enterprise_monthly",  # Replace with actual Stripe price ID
    },
}


@pricing_bp.route("/pricing")
def pricing():
    """Display pricing plans"""
    user_stats = None
    if current_user.is_authenticated:
        from utils.monetization import show_usage_stats

        user_stats = show_usage_stats()

    return render_template(
        "pricing/plans.html", plans=PRICING_PLANS, user_stats=user_stats
    )


@pricing_bp.route("/subscribe/<plan_type>")
@login_required
def subscribe(plan_type):
    """Initialize subscription process"""
    if plan_type not in PRICING_PLANS:
        flash("Invalid subscription plan", "error")
        return redirect(url_for("pricing.pricing"))

    # Check if user already has active subscription
    existing_sub = Subscription.get_user_subscription(current_user.id)
    if existing_sub and existing_sub.is_active:
        flash("You already have an active subscription", "info")
        return redirect(url_for("users.account"))

    plan = PRICING_PLANS[plan_type]

    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": plan["stripe_price_id"],
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=url_for("pricing.subscription_success", _external=True)
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("pricing.pricing", _external=True),
            customer_email=current_user.email,
            metadata={"user_id": current_user.id, "plan_type": plan_type},
        )

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        flash(f"Error creating subscription: {str(e)}", "error")
        return redirect(url_for("pricing.pricing"))


@pricing_bp.route("/subscription/success")
@login_required
def subscription_success():
    """Handle successful subscription"""
    session_id = request.args.get("session_id")

    if not session_id:
        flash("Invalid session", "error")
        return redirect(url_for("pricing.pricing"))

    try:
        # Retrieve the session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status == "paid":
            # Get subscription details
            stripe_subscription = stripe.Subscription.retrieve(
                checkout_session.subscription
            )

            # Create subscription record
            plan_type = checkout_session.metadata.get("plan_type")
            end_date = datetime.fromtimestamp(stripe_subscription.current_period_end)

            subscription = Subscription(
                user_id=current_user.id,
                plan_type=plan_type,
                status="active",
                end_date=end_date,
                stripe_subscription_id=stripe_subscription.id,
            )

            db.session.add(subscription)
            db.session.commit()

            flash(f"Successfully subscribed to {plan_type.title()} plan!", "success")
            return redirect(url_for("users.account"))
        else:
            flash("Payment was not completed", "error")
            return redirect(url_for("pricing.pricing"))

    except Exception as e:
        flash(f"Error processing subscription: {str(e)}", "error")
        return redirect(url_for("pricing.pricing"))


@pricing_bp.route("/subscription/cancel")
@login_required
def cancel_subscription():
    """Cancel user's subscription"""
    subscription = Subscription.get_user_subscription(current_user.id)

    if not subscription or not subscription.is_active:
        flash("No active subscription found", "error")
        return redirect(url_for("users.account"))

    try:
        # Cancel subscription in Stripe
        if subscription.stripe_subscription_id:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id, cancel_at_period_end=True
            )

        # Update local record
        subscription.status = "canceled"
        db.session.commit()

        flash(
            "Subscription canceled. Access will continue until the end of your billing period.",
            "info",
        )

    except Exception as e:
        flash(f"Error canceling subscription: {str(e)}", "error")

    return redirect(url_for("users.account"))


@pricing_bp.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    # Handle the event
    if event["type"] == "customer.subscription.deleted":
        # Subscription was deleted
        subscription_id = event["data"]["object"]["id"]
        local_sub = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()

        if local_sub:
            local_sub.status = "canceled"
            db.session.commit()

    elif event["type"] == "invoice.payment_succeeded":
        # Payment succeeded, extend subscription
        subscription_id = event["data"]["object"]["subscription"]
        local_sub = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()

        if local_sub:
            # Get updated subscription from Stripe
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            local_sub.end_date = datetime.fromtimestamp(stripe_sub.current_period_end)
            local_sub.status = "active"
            db.session.commit()

    elif event["type"] == "invoice.payment_failed":
        # Payment failed
        subscription_id = event["data"]["object"]["subscription"]
        local_sub = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()

        if local_sub:
            local_sub.status = "payment_failed"
            db.session.commit()

    return "Success", 200


@pricing_bp.route("/api/usage-stats")
@login_required
def api_usage_stats():
    """API endpoint for usage statistics"""
    from utils.monetization import show_usage_stats

    return jsonify(show_usage_stats())


@pricing_bp.route("/api/upgrade-prompt")
def api_upgrade_prompt():
    """API endpoint for upgrade prompts"""
    if not current_user.is_authenticated:
        return jsonify(
            {
                "show_prompt": True,
                "title": "Create Account for More Uses",
                "message": "Sign up for a free account to get 5 tool uses per month!",
                "primary_action": {
                    "text": "Sign Up Free",
                    "url": url_for("users.register"),
                },
                "secondary_action": {
                    "text": "View Pricing",
                    "url": url_for("pricing.pricing"),
                },
            }
        )

    subscription = Subscription.get_user_subscription(current_user.id)
    if subscription and subscription.is_active:
        return jsonify({"show_prompt": False})

    from models.tool_usage import ToolUsage

    monthly_usage = ToolUsage.get_monthly_usage(current_user.id)

    if monthly_usage >= 5:
        return jsonify(
            {
                "show_prompt": True,
                "title": "Upgrade to Continue",
                "message": "You've used all 5 of your free monthly tools. Upgrade to Premium for unlimited access!",
                "primary_action": {
                    "text": "Upgrade to Premium",
                    "url": url_for("pricing.subscribe", plan_type="premium"),
                },
                "secondary_action": {
                    "text": "View All Plans",
                    "url": url_for("pricing.pricing"),
                },
            }
        )
    elif monthly_usage >= 3:
        return jsonify(
            {
                "show_prompt": True,
                "title": "Running Low on Credits",
                "message": f"You have {5 - monthly_usage} tool uses remaining this month.",
                "primary_action": {
                    "text": "Upgrade for Unlimited",
                    "url": url_for("pricing.subscribe", plan_type="premium"),
                },
                "secondary_action": {
                    "text": "View Pricing",
                    "url": url_for("pricing.pricing"),
                },
            }
        )

    return jsonify({"show_prompt": False})
