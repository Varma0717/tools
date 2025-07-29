"""
Payment and Checkout Routes for Super SEO Toolkit
Handles Razorpay integration and subscription management
"""

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
)
from flask_login import login_required, current_user
import razorpay
import hashlib
import hmac
import os
import json
from datetime import datetime, timedelta
from . import payment_bp
from app.services.razorpay_handler import payment_handler

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID", "rzp_test_your_key_id"),
        os.getenv("RAZORPAY_KEY_SECRET", "your_secret_key"),
    )
)

# Plan configurations
PLAN_CONFIGS = {
    "free": {
        "name": "Free Plan",
        "price": 0,
        "features": [
            "15+ Essential SEO Tools",
            "5 daily analyses per tool",
            "Basic reports (PDF)",
            "Community support",
            "Basic keyword tracking (10 keywords)",
        ],
        "limits": {"daily_analyses": 5, "keywords": 10, "competitors": 0},
    },
    "professional": {
        "name": "Professional Plan",
        "monthly_price": 29,
        "annual_price": 23,
        "features": [
            "All Starter features",
            "50+ Professional SEO Tools",
            "500 daily analyses per tool",
            "Advanced reports & exports",
            "Priority email support",
            "Competitor analysis (5 competitors)",
            "Keyword tracking (100 keywords)",
            "Historical data access",
            "API access",
        ],
        "limits": {"daily_analyses": 500, "keywords": 100, "competitors": 5},
    },
}


@payment_bp.route("/checkout")
def checkout():
    """Render checkout page"""
    plan = request.args.get("plan", "professional")
    billing = request.args.get("billing", "monthly")

    # Validate plan
    if plan not in PLAN_CONFIGS:
        flash("Invalid plan selected", "error")
        return redirect(url_for("main.pricing"))

    # Free plan doesn't need checkout
    if plan == "free":
        flash("Free plan is already active", "info")
        return redirect(url_for("main.dashboard"))

    return render_template("checkout.html", plan=plan, billing=billing)


@payment_bp.route("/api/payment/create-order", methods=["POST"])
@login_required
def create_payment_order():
    """Create Razorpay order for payment"""
    try:
        data = request.get_json()
        plan = data.get("plan", "professional")
        billing = data.get("billing", "monthly")
        customer_data = data.get("customer_data", {})

        # Validate plan
        if plan not in PLAN_CONFIGS or plan == "free":
            return jsonify({"success": False, "message": "Invalid plan"}), 400

        plan_config = PLAN_CONFIGS[plan]

        # Calculate amount
        if billing == "annual":
            amount = plan_config["annual_price"]
        else:
            amount = plan_config["monthly_price"]

        # Add tax (18% GST)
        tax_amount = round(amount * 0.18, 2)
        total_amount = amount + tax_amount

        # Convert to paisa (Razorpay expects amount in smallest currency unit)
        amount_in_paisa = int(total_amount * 100)

        # Create Razorpay order
        order_data = {
            "amount": amount_in_paisa,
            "currency": "USD",  # Change to 'INR' for Indian Rupees
            "receipt": f"order_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "notes": {
                "plan": plan,
                "billing": billing,
                "user_id": current_user.id,
                "user_email": current_user.email,
            },
        }

        order = razorpay_client.order.create(data=order_data)

        # Store order details in session for verification
        session["pending_order"] = {
            "order_id": order["id"],
            "plan": plan,
            "billing": billing,
            "amount": total_amount,
            "customer_data": customer_data,
        }

        return jsonify(
            {
                "success": True,
                "order_id": order["id"],
                "amount": amount_in_paisa,
                "currency": order["currency"],
                "key": os.getenv("RAZORPAY_KEY_ID"),
            }
        )

    except Exception as e:
        print(f"Payment order creation error: {e}")
        return (
            jsonify({"success": False, "message": "Failed to create payment order"}),
            500,
        )


@payment_bp.route("/api/payment/success", methods=["POST"])
@login_required
def payment_success():
    """Handle successful payment verification"""
    try:
        data = request.get_json()
        payment_id = data.get("payment_id")
        order_id = data.get("order_id")
        signature = data.get("signature")

        # Get pending order from session
        pending_order = session.get("pending_order")
        if not pending_order or pending_order["order_id"] != order_id:
            return jsonify({"success": False, "message": "Invalid order"}), 400

        # Verify payment signature
        if not verify_payment_signature(payment_id, order_id, signature):
            return (
                jsonify({"success": False, "message": "Payment verification failed"}),
                400,
            )

        # Update user subscription using the handler
        payment_record = payment_handler.create_payment_record(
            current_user.id,
            payment_id,
            order_id,
            pending_order["amount"],
            pending_order["plan"],
            pending_order["billing"],
        )

        subscription = payment_handler.update_user_subscription(
            current_user.id,
            pending_order["plan"],
            pending_order["billing"],
            payment_record.id if payment_record else None,
        )

        if subscription:
            # Clear pending order from session
            session.pop("pending_order", None)

            # Store payment details for success page
            session["last_payment"] = {
                "payment_id": payment_id,
                "plan": pending_order["plan"],
                "billing": pending_order["billing"],
                "amount": pending_order["amount"],
            }

            return jsonify(
                {
                    "success": True,
                    "redirect_url": f"/payment/success?payment_id={payment_id}",
                }
            )
        else:
            return (
                jsonify({"success": False, "message": "Failed to update subscription"}),
                500,
            )

    except Exception as e:
        print(f"Payment success handling error: {e}")
        return jsonify({"success": False, "message": "Payment processing failed"}), 500


@payment_bp.route("/payment/success")
@login_required
def payment_success_page():
    """Render payment success page"""
    payment_id = request.args.get("payment_id")
    last_payment = session.get("last_payment")

    if not payment_id or not last_payment:
        flash("Payment information not found", "error")
        return redirect(url_for("main.dashboard"))

    # Calculate next billing date
    if last_payment["billing"] == "annual":
        next_billing = datetime.now() + timedelta(days=365)
    else:
        next_billing = datetime.now() + timedelta(days=30)

    return render_template(
        "payment_success.html",
        payment_id=payment_id,
        plan_name=PLAN_CONFIGS[last_payment["plan"]]["name"],
        billing_type=last_payment["billing"].title(),
        amount_paid=f"${last_payment['amount']:.2f}",
        next_billing_date=next_billing.strftime("%B %d, %Y"),
    )


def verify_payment_signature(payment_id, order_id, signature):
    """Verify Razorpay payment signature"""
    try:
        # Create signature verification string
        body = f"{order_id}|{payment_id}"

        # Generate expected signature
        expected_signature = hmac.new(
            os.getenv("RAZORPAY_KEY_SECRET", "").encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return signature == expected_signature
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False


def update_user_subscription(user_id, plan, billing, payment_id, order_id, amount):
    """Update user subscription in database"""
    try:
        # Import here to avoid circular imports
        from app.models.user import User
        from app.models.subscription import Subscription
        from app.models.payment import Payment
        from app.core.extensions import db

        user = User.query.get(user_id)
        if not user:
            return False

        # Create payment record
        payment = Payment(
            user_id=user_id,
            razorpay_payment_id=payment_id,
            razorpay_order_id=order_id,
            amount=amount,
            currency="USD",
            status="completed",
            payment_method="razorpay",
        )
        db.session.add(payment)

        # Update or create subscription
        subscription = Subscription.query.filter_by(user_id=user_id).first()

        if subscription:
            # Update existing subscription
            subscription.plan = plan
            subscription.billing_cycle = billing
            subscription.status = "active"
            subscription.current_period_start = datetime.utcnow()

            if billing == "annual":
                subscription.current_period_end = datetime.utcnow() + timedelta(
                    days=365
                )
            else:
                subscription.current_period_end = datetime.utcnow() + timedelta(days=30)

        else:
            # Create new subscription
            end_date = datetime.utcnow() + timedelta(
                days=365 if billing == "annual" else 30
            )

            subscription = Subscription(
                user_id=user_id,
                plan=plan,
                billing_cycle=billing,
                status="active",
                current_period_start=datetime.utcnow(),
                current_period_end=end_date,
            )
            db.session.add(subscription)

        # Update user plan
        user.plan = plan

        db.session.commit()
        return True

    except Exception as e:
        print(f"Subscription update error: {e}")
        db.session.rollback()
        return False


# Register the blueprint
def register_payment_routes(app):
    """Register payment routes with the Flask app"""
    app.register_blueprint(payment_bp)
