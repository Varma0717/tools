from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from datetime import datetime, date
from app.blueprints.users.forms import ProfileForm
from app.models.user import User
from app.models.order import Order, Download
from app.models.setting import Setting
from app.core.extensions import db
from app.utils.payment import create_order


users_bp = Blueprint("users", __name__, url_prefix="/users")


# ------------------------------
# ✅ MAIN CUSTOMER ACCOUNT PAGE (WooCommerce-style layout)
@users_bp.route("/account")
@login_required
def account():
    if current_user.role != "customer":
        return redirect(url_for("admin.settings"))

    # Calculate comprehensive user statistics for the account page
    user_stats = {
        "tools_used": current_user.daily_tool_usage or 0,
        "reports_generated": min(
            current_user.daily_tool_usage or 0, 50
        ),  # Estimate based on tool usage
        "account_days": (
            date.today() - (current_user.last_usage_reset or date.today())
        ).days
        + 1,
        "package_type": current_user.get_package_display_name(),
        "is_pro": current_user.is_pro_user(),
        "usage_limit": current_user.get_tool_usage_limit(),
        "subscription_active": current_user.subscription_active,
        "username": current_user.first_name or current_user.username,
    }

    return render_template("users/account.html", user_stats=user_stats)


# ------------------------------
# ✅ DASHBOARD - Package-aware user dashboard
@users_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard with package-specific interface"""
    if current_user.role != "customer":
        return redirect(url_for("admin.settings"))

    # SEO functionality removed - coming soon
    recent_reports = []
    total_reports = 0
    avg_score = 0
    if recent_reports:
        scores = [
            report.overall_score for report in recent_reports if report.overall_score
        ]
        avg_score = sum(scores) / len(scores) if scores else 0

    # Get user statistics
    user_stats = {
        "daily_usage": current_user.daily_tool_usage or 0,
        "package_type": current_user.get_package_display_name(),
        "is_pro": current_user.is_pro_user(),
        "usage_limit": current_user.get_tool_usage_limit(),
        "tools_used": current_user.daily_tool_usage or 0,
        "reports_generated": total_reports or 0,  # Use actual reports count
        "account_days": (
            date.today() - (current_user.last_usage_reset or date.today())
        ).days
        + 1,
        "username": current_user.first_name or current_user.username,
        "subscription_active": current_user.subscription_active,
        "avg_seo_score": round(avg_score),
        "recent_reports": recent_reports,
        "total_reports": total_reports,
    }

    return render_template("users/dashboard.html", stats=user_stats)


# ------------------------------
# ✅ AJAX PARTIAL LOADS (WooCommerce Tabs)
@users_bp.route("/account/<section>")
@login_required
def account_section(section):
    if current_user.role != "customer":
        return redirect(url_for("admin.settings"))

    # Calculate user statistics for all sections
    user_stats = {
        "tools_used": current_user.daily_tool_usage or 0,
        "reports_generated": min(current_user.daily_tool_usage or 0, 50),
        "account_days": (
            date.today() - (current_user.last_usage_reset or date.today())
        ).days
        + 1,
        "package_type": current_user.get_package_display_name(),
        "is_pro": current_user.is_pro_user(),
        "usage_limit": current_user.get_tool_usage_limit(),
    }

    section_map = {
        "overview": "users/sections/overview.html",
        "orders": "users/sections/orders.html",
        "downloads": "users/sections/downloads.html",
        "profile": "users/sections/profile.html",
        "logout": None,
    }

    template = section_map.get(section)

    if not template and section != "logout":
        return "Section not found", 404

    if section == "orders":
        orders = current_user.orders
        return render_template(
            template, user=current_user, orders=orders, user_stats=user_stats
        )

    elif section == "downloads":
        downloads = current_user.downloads
        return render_template(
            template, user=current_user, downloads=downloads, user_stats=user_stats
        )

    elif section == "profile":
        from app.blueprints.users.forms import ProfileForm

        form = ProfileForm(obj=current_user)
        return render_template(
            template, user=current_user, form=form, user_stats=user_stats
        )

    elif section == "logout":
        return redirect(url_for("auth.logout"))

    return render_template(template, user=current_user, user_stats=user_stats)


# ------------------------------
# ✅ PROFILE UPDATE POST AJAX
@users_bp.route("/account/profile", methods=["POST"])
@login_required
def save_profile():
    from app.blueprints.users.forms import ProfileForm

    form = ProfileForm()

    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        return render_template("users/sections/profile.html", form=form)

    return render_template("users/sections/profile.html", form=form), 400


# ------------------------------
# ✅ PREMIUM UPGRADE PAGE
@users_bp.route("/upgrade")
@login_required
def upgrade():
    user_data = {
        "is_pro": current_user.is_pro_user(),
        "package_type": current_user.get_package_display_name(),
        "daily_usage": current_user.daily_tool_usage or 0,
        "usage_limit": current_user.get_tool_usage_limit(),
    }
    return render_template("users/upgrade.html", user_data=user_data)


# ------------------------------
# ✅ PAYMENT HANDLING
@users_bp.route("/payment", methods=["POST"])
@login_required
def payment():
    amount = int(request.form.get("amount", 0))
    try:
        order = create_order(amount)
        current_user.is_premium = True
        db.session.commit()
        flash("Payment successful! You are now a premium user.", "success")
    except Exception as e:
        flash(f"Payment failed: {str(e)}", "danger")
    return redirect(url_for("users.account"))


# ------------------------------
# ✅ PROFILE PAGE
@users_bp.route("/profile")
@login_required
def profile():
    """User profile page"""
    if current_user.role != "customer":
        return redirect(url_for("admin.settings"))
    return render_template("users/profile.html")


# ------------------------------
# ✅ SETTINGS PAGE
@users_bp.route("/settings")
@login_required
def settings():
    """User settings page"""
    if current_user.role != "customer":
        return redirect(url_for("admin.settings"))
    return render_template("users/settings.html")


# ------------------------------
# ✅ BILLING PAGE
@users_bp.route("/billing")
@login_required
def billing():
    """User billing page"""
    if current_user.role != "customer":
        return redirect(url_for("admin.settings"))
    return render_template("users/billing.html")
