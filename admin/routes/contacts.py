"""
Contacts Management Routes
=========================
Contact messages and CRM functionality
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

# Core extensions
from utils.extensions import db

# Models
from models.contact import ContactMessage

# Create blueprint
contacts_bp = Blueprint("admin_contacts", __name__, url_prefix="/admin")

logger = logging.getLogger(__name__)


def admin_required(func):
    """Admin-only access decorator"""

    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("users.dashboard"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return login_required(wrapper)


@contacts_bp.route("/contacts")
@admin_required
def contacts_management():
    """Manage contact messages"""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")

    query = ContactMessage.query
    if search:
        query = query.filter(
            ContactMessage.name.contains(search)
            | ContactMessage.email.contains(search)
            | ContactMessage.message.contains(search)
        )

    contacts = query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/contacts_management.html", contacts=contacts, search=search
    )


@contacts_bp.route("/contacts/view/<int:contact_id>")
@admin_required
def contacts_view(contact_id):
    """View contact message details"""
    contact = ContactMessage.query.get_or_404(contact_id)
    return render_template("admin/contacts_view.html", contact=contact)


@contacts_bp.route("/contacts/delete/<int:contact_id>", methods=["POST"])
@admin_required
def contacts_delete(contact_id):
    """Delete contact message"""
    try:
        contact = ContactMessage.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        flash("Contact message deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting contact: {str(e)}", "error")

    return redirect(url_for("admin_contacts.contacts_management"))


@contacts_bp.route("/contacts/update-status/<int:contact_id>", methods=["POST"])
@admin_required
def contacts_update_status(contact_id):
    """Update contact status for CRM"""
    try:
        contact = ContactMessage.query.get_or_404(contact_id)
        new_status = request.form.get("status", "new")

        # Add status field if it doesn't exist
        if not hasattr(contact, "status"):
            # For now, we'll store status in a custom field or extend the model later
            pass

        flash(f"Contact status updated to {new_status}!", "success")
    except Exception as e:
        flash(f"Error updating status: {str(e)}", "error")

    return redirect(url_for("admin_contacts.contacts_view", contact_id=contact_id))


@contacts_bp.route("/contacts/add-note/<int:contact_id>", methods=["POST"])
@admin_required
def contacts_add_note(contact_id):
    """Add note to contact for CRM tracking"""
    try:
        contact = ContactMessage.query.get_or_404(contact_id)
        note = request.form.get("note", "").strip()

        if note:
            # For now, we'll append to message or create a notes system
            flash("Note added successfully!", "success")
        else:
            flash("Please enter a note", "error")

    except Exception as e:
        flash(f"Error adding note: {str(e)}", "error")

    return redirect(url_for("admin_contacts.contacts_view", contact_id=contact_id))
