from flask import Blueprint, redirect, url_for, flash
from flask_dance.contrib.google import google
from flask_login import login_user, current_user
from utils.extensions import db
from users.models.user import User
from datetime import datetime
import re

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def generate_unique_username(base_username):
    """Generate a unique username from base username"""
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


# Trigger Google OAuth login
@auth_bp.route("/google")
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("auth.google_callback"))


# Handle Google OAuth callback
@auth_bp.route("/google/callback")
def google_callback():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    if not google.authorized:
        flash("Google authentication failed. Please try again.", "danger")
        return redirect(url_for("users.login"))

    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to retrieve user information from Google.", "danger")
            return redirect(url_for("users.login"))

        userinfo = resp.json()
        email = userinfo.get("email")
        name = userinfo.get("name", "")

        if not email:
            flash("Could not retrieve email from Google. Please try again.", "danger")
            return redirect(url_for("users.login"))

        # Check if user exists
        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            # Create new user
            username = generate_unique_username(name or email.split("@")[0])
            user = User(
                email=email.lower(),
                username=username,
                password="oauth_google",  # placeholder for OAuth users
                role="customer",
                email_verified=True,  # Google emails are pre-verified
                first_name=name.split()[0] if name and " " in name else name,
                last_name=(
                    name.split()[-1]
                    if name and " " in name and len(name.split()) > 1
                    else None
                ),
            )
            db.session.add(user)
            db.session.commit()
            flash(
                "Welcome to Super SEO Toolkit! Your account has been created successfully.",
                "success",
            )
        else:
            flash("Welcome back!", "success")

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user)
        return redirect(url_for("users.account"))

    except Exception as e:
        flash(
            "An error occurred during Google authentication. Please try again.",
            "danger",
        )
        return redirect(url_for("users.login"))
