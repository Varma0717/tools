"""
Users Management Routes
======================
User CRUD operations and management functionality
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

# Core extensions
from utils.extensions import db

# Models
from users.models.user import User

# Create blueprint
users_bp = Blueprint("admin_users", __name__, url_prefix="/admin")

logger = logging.getLogger(__name__)


def admin_required(func):
    """Admin-only access decorator"""

    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("users.dashboard"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return login_required(wrapper)


@users_bp.route("/users")
@admin_required
def users_management():
    """Comprehensive user management with CRUD"""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    role_filter = request.args.get("role", "")
    status_filter = request.args.get("status", "")

    # Build query
    query = User.query

    if search:
        query = query.filter(
            User.username.contains(search) | User.email.contains(search)
        )

    if role_filter:
        query = query.filter(User.role == role_filter)

    if status_filter == "active":
        query = query.filter(User.is_active == True)
    elif status_filter == "inactive":
        query = query.filter(User.is_active == False)

    users = query.paginate(page=page, per_page=20, error_out=False)
    user_stats = get_user_statistics()

    return render_template(
        "admin/users_management.html",
        users=users,
        stats=user_stats,
        search=search,
        role_filter=role_filter,
        status_filter=status_filter,
    )


@users_bp.route("/users/create", methods=["GET", "POST"])
@admin_required
def users_create():
    """Create new user"""
    if request.method == "POST":
        try:
            user_data = {
                "username": request.form.get("username"),
                "email": request.form.get("email"),
                "password": request.form.get("password"),  # Should be hashed
                "role": request.form.get("role", "customer"),
                "is_active": request.form.get("is_active") == "on",
            }

            # Check if user exists
            if User.query.filter_by(email=user_data["email"]).first():
                flash("User with this email already exists!", "error")
                return redirect(url_for("admin_users.users_create"))

            if User.query.filter_by(username=user_data["username"]).first():
                flash("Username already taken!", "error")
                return redirect(url_for("admin_users.users_create"))

            # Create user (password should be hashed in production)
            new_user = User(**user_data)
            db.session.add(new_user)
            db.session.commit()

            flash("User created successfully!", "success")
            return redirect(url_for("admin_users.users_management"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating user: {str(e)}", "error")

    return render_template("admin/users_create.html")


@users_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@admin_required
def users_edit(user_id):
    """Edit existing user"""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        try:
            user.username = request.form.get("username")
            user.email = request.form.get("email")
            user.role = request.form.get("role")
            user.is_active = request.form.get("is_active") == "on"

            db.session.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for("admin_users.users_management"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating user: {str(e)}", "error")

    return render_template("admin/users_edit.html", user=user)


@users_bp.route("/users/delete/<int:user_id>", methods=["POST"])
@admin_required
def users_delete(user_id):
    """Delete user"""
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "error")

    return redirect(url_for("admin_users.users_management"))


@users_bp.route("/api/user/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "status": "active" if user.is_active else "inactive",
                "message": f'User {user.username} is now {"active" if user.is_active else "inactive"}',
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@users_bp.route("/api/user/<int:user_id>/change-role", methods=["POST"])
@admin_required
def change_user_role(user_id):
    """Change user role"""
    try:
        user = User.query.get_or_404(user_id)
        new_role = request.json.get("role")

        if new_role not in ["customer", "admin", "moderator"]:
            return jsonify({"success": False, "message": "Invalid role"}), 400

        user.role = new_role
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "role": user.role,
                "message": f"User {user.username} role changed to {new_role}",
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


def get_user_statistics():
    """Get detailed user statistics"""
    from datetime import datetime, timedelta

    try:
        # Role distribution
        role_stats = (
            db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
        )

        # Registration trends (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        registration_trend = (
            db.session.query(func.date(User.created_at), func.count(User.id))
            .filter(User.created_at >= thirty_days_ago)
            .group_by(func.date(User.created_at))
            .all()
        )

        return {
            "role_distribution": dict(role_stats),
            "registration_trend": dict(registration_trend),
            "total_users": User.query.count(),
        }
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        return {}
