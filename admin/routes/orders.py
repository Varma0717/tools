"""
Orders Management Routes
=======================
Order management and subscription functionality
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

# Core extensions
from utils.extensions import db

# Models
from users.models.order import Order
from users.models.user import User
from models.subscription import SubscriptionPlan, UserSubscription

# Create blueprint
orders_bp = Blueprint("admin_orders", __name__, url_prefix="/admin")

logger = logging.getLogger(__name__)


def admin_required(func):
    """Admin-only access decorator"""

    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("users.dashboard"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return login_required(wrapper)


@orders_bp.route("/orders")
@admin_required
def orders_management():
    """Manage orders"""
    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "")

    query = Order.query
    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/orders_management.html", orders=orders, status_filter=status_filter
    )


@orders_bp.route("/orders/view/<int:order_id>")
@admin_required
def orders_view(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    return render_template("admin/orders_view.html", order=order)


@orders_bp.route("/subscriptions")
@admin_required
def subscriptions_management():
    """Manage subscription plans and user subscriptions"""
    plans = SubscriptionPlan.query.all()
    user_subscriptions = UserSubscription.query.join(User).all()

    return render_template(
        "admin/subscriptions_management.html",
        plans=plans,
        user_subscriptions=user_subscriptions,
    )


@orders_bp.route("/subscriptions/plans/create", methods=["GET", "POST"])
@admin_required
def subscription_plans_create():
    """Create new subscription plan"""
    if request.method == "POST":
        try:
            plan = SubscriptionPlan(
                name=request.form.get("name"),
                price=float(request.form.get("price", 0)),
                billing_cycle=request.form.get("billing_cycle"),
                max_daily_usage=int(request.form.get("max_daily_usage", 10)),
                max_reports=int(request.form.get("max_reports", 5)),
                features=request.form.get("features", "").split(","),
                is_active=request.form.get("is_active") == "on",
            )
            db.session.add(plan)
            db.session.commit()
            flash("Subscription plan created successfully!", "success")
            return redirect(url_for("admin_orders.subscriptions_management"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating plan: {str(e)}", "error")

    return render_template("admin/subscription_plans_create.html")
