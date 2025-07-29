from flask import (
    Blueprint,
    redirect,
    url_for,
    render_template,
    request,
    flash,
    session,
    jsonify,
)
from flask_dance.contrib.google import google
from flask_login import login_user, current_user
from flask_wtf.csrf import generate_csrf, validate_csrf, CSRFError
from werkzeug.security import check_password_hash
import requests
from app.core.extensions import db, oauth
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# CSRF error handler
@auth_bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("Security token expired. Please try again.", "danger")
    return redirect(request.url)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page with enhanced features"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        try:
            # Validate CSRF token first
            validate_csrf(request.form.get("csrf_token"))

            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            terms_accepted = request.form.get("terms") == "on"
            newsletter_signup = request.form.get("newsletter") == "on"

            # Enhanced validation
            errors = []

            if not username or not email or not password:
                errors.append("All fields are required.")

            if len(username) < 3 or len(username) > 20:
                errors.append("Username must be 3-20 characters long.")

            if not username.replace("_", "").isalnum():
                errors.append(
                    "Username can only contain letters, numbers, and underscores."
                )

            if len(password) < 8:
                errors.append("Password must be at least 8 characters long.")

            if password != confirm_password:
                errors.append("Passwords do not match.")

            if not terms_accepted:
                errors.append("You must accept the terms and conditions.")

            # Check if user already exists
            if User.query.filter_by(email=email).first():
                errors.append("Email already exists. Please use a different email.")

            if User.query.filter_by(username=username).first():
                errors.append(
                    "Username already exists. Please use a different username."
                )

            if errors:
                for error in errors:
                    flash(error, "danger")
                csrf_token = generate_csrf()
                return render_template("auth/register.html", csrf_token=csrf_token)

            # Create new user
            from werkzeug.security import generate_password_hash

            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role="customer",
            )

            # Add newsletter preference if available
            if hasattr(user, "newsletter_subscribed"):
                user.newsletter_subscribed = newsletter_signup

            db.session.add(user)
            db.session.commit()

            flash("Registration successful! Welcome to Super SEO Toolkit!", "success")

            # Auto-login the user
            login_user(user)
            return redirect(url_for("main.home"))

        except CSRFError:
            flash("Security token expired. Please try again.", "danger")
            csrf_token = generate_csrf()
            return render_template("auth/register.html", csrf_token=csrf_token)
        except Exception as e:
            db.session.rollback()
            flash("Registration failed. Please try again.", "danger")
            csrf_token = generate_csrf()
            return render_template("auth/register.html", csrf_token=csrf_token)

    csrf_token = generate_csrf()
    return render_template("auth/register.html", csrf_token=csrf_token)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login page with enhanced features"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        try:
            # Validate CSRF token first
            validate_csrf(request.form.get("csrf_token"))

            username = request.form.get(
                "email", ""
            ).strip()  # Field name is 'email' in form
            password = request.form.get("password", "")
            remember_me = request.form.get("remember_me") == "on"

            if not username or not password:
                flash("Please enter both email/username and password.", "danger")
                csrf_token = generate_csrf()
                return render_template("auth/login.html", csrf_token=csrf_token)

            # Find user by username or email
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()

            if user:
                # Check if password matches
                if check_password_hash(user.password, password):
                    # Login with remember me option
                    login_user(user, remember=remember_me)
                    flash(f"Welcome back, {user.username}!", "success")

                    # Redirect to requested page or home
                    next_page = request.args.get("next")
                    return (
                        redirect(next_page)
                        if next_page
                        else redirect(url_for("main.home"))
                    )
                else:
                    flash("Invalid password. Please try again.", "danger")
            else:
                flash("No account found with that email/username.", "danger")

        except CSRFError:
            flash("Security token expired. Please try again.", "danger")
        except Exception as e:
            flash("Login failed. Please try again.", "danger")

    csrf_token = generate_csrf()
    return render_template("auth/login.html", csrf_token=csrf_token)


@auth_bp.route("/logout")
def logout():
    """User logout"""
    from flask_login import logout_user

    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Password reset request"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = User.query.filter_by(email=email).first()

        if user:
            # In a real implementation, you would:
            # 1. Generate a secure reset token
            # 2. Send an email with reset link
            # 3. Store token in database with expiration
            flash(
                "If an account with that email exists, you will receive password reset instructions.",
                "info",
            )
        else:
            flash(
                "If an account with that email exists, you will receive password reset instructions.",
                "info",
            )

        return redirect(url_for("auth.login"))

    csrf_token = generate_csrf()
    return render_template("auth/forgot_password.html", csrf_token=csrf_token)


# Trigger login
@auth_bp.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("auth.google_callback"))


# Handle Google callback
@auth_bp.route("/google/callback")
def google_callback():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info from Google", 400

    userinfo = resp.json()
    email = userinfo.get("email")
    name = userinfo.get("name") or email.split("@")[0]

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            username=name,
            password="oauth_google",  # placeholder
            role="customer",
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("users.account"))


# GitHub OAuth routes
@auth_bp.route("/github")
def github_login():
    """Initiate GitHub OAuth login"""
    # For now, redirect to coming soon message
    flash("GitHub login will be available soon! Please use email or Google.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/github/callback")
def github_callback():
    """Handle GitHub OAuth callback"""
    # Placeholder for GitHub OAuth implementation
    flash("GitHub login is coming soon!", "info")
    return redirect(url_for("auth.login"))
