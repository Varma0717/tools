from flask import Blueprint, redirect, url_for
from flask_dance.contrib.google import google
from flask_login import login_user
from utils.extensions import db, oauth
from users.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

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
            role="customer"
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("users.account"))
