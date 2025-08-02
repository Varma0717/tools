from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    session,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from users.forms import (
    LoginForm,
    ProfileForm,
    RegistrationForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from users.models.user import User
from users.models.order import Order
from users.models.download import Download
from admin.models import Setting
from utils.extensions import db
from utils.payment import create_order
from flask_dance.contrib.google import google
from datetime import datetime, timedelta
import requests
import re
import secrets
from flask_mail import Message
from utils.extensions import mail

users_bp = Blueprint("users", __name__, url_prefix="/users")

# Rate limiting dictionary (in production, use Redis)
login_attempts = {}


def is_rate_limited(ip_address):
    """Check if IP is rate limited"""
    now = datetime.utcnow()
    if ip_address in login_attempts:
        attempts, last_attempt = login_attempts[ip_address]
        # If last attempt was more than 15 minutes ago, reset counter
        if now - last_attempt > timedelta(minutes=15):
            del login_attempts[ip_address]
            return False
        # If more than 10 attempts in 15 minutes, rate limit
        if attempts >= 10:
            return True
    return False


def record_login_attempt(ip_address):
    """Record a login attempt"""
    now = datetime.utcnow()
    if ip_address in login_attempts:
        attempts, _ = login_attempts[ip_address]
        login_attempts[ip_address] = (attempts + 1, now)
    else:
        login_attempts[ip_address] = (1, now)


# ------------------------------
# ✅ ENHANCED LOGIN WITH SECURITY
@users_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if current_user.is_authenticated:
        # Already logged in users go to correct dashboard
        return redirect(
            url_for(
                "users.account" if current_user.role == "customer" else "admin.panel"
            )
        )

    form = LoginForm()
    error = None
    ip_address = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)

    # Check for rate limiting
    if is_rate_limited(ip_address):
        flash("Too many login attempts. Please try again in 15 minutes.", "danger")
        return render_template("users/login.html", form=form, error="Rate limited")

    if form.validate_on_submit():
        # Record login attempt for rate limiting
        record_login_attempt(ip_address)

        # Find user by username or email
        user = User.query.filter(
            (User.username == form.username.data.strip())
            | (User.email == form.username.data.strip())
        ).first()

        if user:
            # Check if account is locked
            if user.is_account_locked():
                flash(
                    "Account is temporarily locked due to too many failed login attempts. Please try again later.",
                    "danger",
                )
                return render_template(
                    "users/login.html", form=form, error="Account locked"
                )

            # Check if account is active
            if not user.is_active:
                flash(
                    "Your account has been deactivated. Please contact support.",
                    "danger",
                )
                return render_template(
                    "users/login.html", form=form, error="Account inactive"
                )

            # Verify password
            if user.check_password(form.password.data):
                # Successful login
                user.reset_failed_attempts()
                user.last_login = datetime.utcnow()
                db.session.commit()

                login_user(user, remember=form.remember_me.data)
                flash("Login successful! Welcome back.", "success")

                # Redirect to next page or dashboard
                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)

                if user.role == "customer":
                    return redirect(url_for("users.account"))
                else:
                    return redirect(url_for("admin.panel"))
            else:
                # Failed password
                user.increment_failed_attempts()
                error = "Invalid username/email or password."
                flash(error, "danger")
        else:
            # User not found
            error = "Invalid username/email or password."
            flash(error, "danger")

    return render_template("users/login.html", form=form, error=error)


# ------------------------------
# ✅ ENHANCED REGISTRATION WITH VALIDATION
@users_bp.route("/register", methods=["GET", "POST"], endpoint="register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()
    recaptcha_site_key = Setting.query.filter_by(key="recaptcha_site_key").first()

    if form.validate_on_submit():
        # Check reCAPTCHA if enabled
        if recaptcha_site_key:
            recaptcha_response = request.form.get("g-recaptcha-response")
            secret_key = Setting.query.filter_by(key="recaptcha_secret_key").first()

            if secret_key and not verify_recaptcha(
                recaptcha_response, secret_key.value
            ):
                flash("reCAPTCHA verification failed. Please try again.", "danger")
                return render_template(
                    "users/register.html",
                    form=form,
                    recaptcha_site_key=(
                        recaptcha_site_key.value if recaptcha_site_key else None
                    ),
                )

        try:
            # Create new user
            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
                role="customer",
            )
            user.set_password(form.password.data)

            # Generate email verification token
            verification_token = user.generate_email_verification_token()

            db.session.add(user)
            db.session.commit()

            # Send verification email (if mail is configured)
            try:
                send_verification_email(user.email, verification_token)
                flash(
                    "Registration successful! Please check your email to verify your account.",
                    "success",
                )
            except Exception as e:
                # If email fails, still allow registration but warn user
                flash(
                    "Registration successful! However, we couldn't send a verification email. You can still log in.",
                    "warning",
                )

            return redirect(url_for("users.login"))

        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            return render_template(
                "users/register.html",
                form=form,
                recaptcha_site_key=(
                    recaptcha_site_key.value if recaptcha_site_key else None
                ),
            )

    return render_template(
        "users/register.html",
        form=form,
        recaptcha_site_key=recaptcha_site_key.value if recaptcha_site_key else None,
    )


# ------------------------------
# ✅ EMAIL VERIFICATION
@users_bp.route("/verify-email/<token>")
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    if user and user.verify_email_token(token):
        flash("Email verified successfully! You can now log in.", "success")
        return redirect(url_for("users.login"))
    else:
        flash("Invalid or expired verification token.", "danger")
        return redirect(url_for("users.login"))


# ------------------------------
# ✅ FORGOT PASSWORD
@users_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            # Generate reset token
            reset_token = user.generate_password_reset_token()

            # Send reset email
            try:
                send_password_reset_email(user.email, reset_token)
                flash(
                    "Password reset instructions have been sent to your email.", "info"
                )
            except Exception as e:
                flash("Error sending email. Please try again later.", "danger")
        else:
            # Don't reveal if email exists or not for security
            flash(
                "If your email is registered, you will receive password reset instructions.",
                "info",
            )

        return redirect(url_for("users.login"))

    return render_template("users/forgot_password.html", form=form)


# ------------------------------
# ✅ RESET PASSWORD
@users_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    user = User.query.filter_by(password_reset_token=token).first()
    if not user or not user.verify_password_reset_token(token):
        flash("Invalid or expired reset token.", "danger")
        return redirect(url_for("users.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_password_reset_token()
        flash(
            "Your password has been reset successfully. You can now log in.", "success"
        )
        return redirect(url_for("users.login"))

    return render_template("users/reset_password.html", form=form)


# ------------------------------
# ✅ GOOGLE OAUTH LOGIN SUCCESS
@users_bp.route("/login/success")
def login_success():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to authenticate with Google. Please try again.", "danger")
        return redirect(url_for("users.login"))

    userinfo = resp.json()
    email = userinfo.get("email")
    name = userinfo.get("name", email.split("@")[0] if email else "")

    if not email:
        flash("Could not retrieve email from Google. Please try again.", "danger")
        return redirect(url_for("users.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        # Create new user from Google OAuth
        user = User(
            email=email,
            username=generate_unique_username(name or email.split("@")[0]),
            password="oauth_google",  # placeholder - they won't use password login
            role="customer",
            email_verified=True,  # Google emails are verified
        )
        db.session.add(user)
        db.session.commit()
        flash(
            "Account created successfully with Google! Welcome to Super SEO Toolkit.",
            "success",
        )
    else:
        flash("Welcome back!", "success")

    user.last_login = datetime.utcnow()
    db.session.commit()
    login_user(user)
    return redirect(url_for("users.account"))


# ------------------------------
# ✅ MAIN CUSTOMER ACCOUNT PAGE
@users_bp.route("/account")
@login_required
def account():
    if current_user.role != "customer":
        return redirect(url_for("admin.panel"))
    return render_template("users/account.html")


# ------------------------------
# ✅ ACCOUNT SECTIONS
@users_bp.route("/account/<section>")
@login_required
def account_section(section):
    if current_user.role != "customer":
        return redirect(url_for("admin.panel"))

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
        return render_template(template, user=current_user, orders=orders)
    elif section == "downloads":
        downloads = current_user.downloads
        return render_template(template, user=current_user, downloads=downloads)
    elif section == "profile":
        form = ProfileForm(obj=current_user, original_email=current_user.email)
        return render_template(template, user=current_user, form=form)
    elif section == "logout":
        return redirect(url_for("users.logout"))

    return render_template(template, user=current_user)


# ------------------------------
# ✅ PROFILE UPDATE
@users_bp.route("/account/profile", methods=["POST"])
@login_required
def save_profile():
    form = ProfileForm(original_email=current_user.email)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return render_template(
            "users/sections/profile.html", form=form, user=current_user
        )

    return (
        render_template("users/sections/profile.html", form=form, user=current_user),
        400,
    )


# ------------------------------
# ✅ LOGOUT
@users_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    session.clear()  # Clear all session data
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("users.login"))


# ------------------------------
# ✅ PREMIUM UPGRADE PAGE
@users_bp.route("/upgrade")
@login_required
def upgrade():
    return render_template("users/upgrade.html")


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
# UTILITY FUNCTIONS
# ------------------------------


def verify_recaptcha(response, secret_key):
    """Verify reCAPTCHA response"""
    try:
        verify_response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret_key, "response": response},
            timeout=10,
        )
        result = verify_response.json()
        return result.get("success", False)
    except:
        return False


def generate_unique_username(base_username):
    """Generate a unique username"""
    username = re.sub(r"[^a-zA-Z0-9_]", "", base_username.lower())[:20]
    if not username:
        username = "user"

    # Check if username exists and append number if needed
    counter = 0
    original_username = username
    while User.query.filter_by(username=username).first():
        counter += 1
        username = f"{original_username}{counter}"

    return username


def send_verification_email(email, token):
    """Send email verification email"""
    msg = Message("Verify Your Email - Super SEO Toolkit", recipients=[email])
    verify_url = url_for("users.verify_email", token=token, _external=True)
    msg.html = render_template("emails/verify_email.html", verify_url=verify_url)
    mail.send(msg)


def send_password_reset_email(email, token):
    """Send password reset email"""
    msg = Message("Reset Your Password - Super SEO Toolkit", recipients=[email])
    reset_url = url_for("users.reset_password", token=token, _external=True)
    msg.html = render_template("emails/reset_password.html", reset_url=reset_url)
    mail.send(msg)


# ------------------------------
# ✅ PROFILE MANAGEMENT
@users_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data.strip()
        current_user.email = form.email.data.strip().lower()
        current_user.first_name = (
            form.first_name.data.strip() if form.first_name.data else None
        )
        current_user.last_name = (
            form.last_name.data.strip() if form.last_name.data else None
        )

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("users.account"))
        except Exception as e:
            db.session.rollback()
            flash("Error updating profile. Please try again.", "danger")

    # Pre-populate form with current user data
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name

    return render_template("users/profile.html", form=form)


@users_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash("Password changed successfully!", "success")
        return redirect(url_for("users.account"))

    return render_template("users/change_password.html", form=form)
