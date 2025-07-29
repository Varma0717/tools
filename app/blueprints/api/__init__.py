"""
API routes for the Flask application.
Contains API endpoints for AJAX requests.
"""

import re
from flask import Blueprint, request, jsonify

from app.core.extensions import db, csrf
from app.models.newsletter import Subscriber

api_bp = Blueprint("api", __name__)


@api_bp.route("/subscribe", methods=["POST"])
@csrf.exempt
def subscribe():
    """Newsletter subscription endpoint."""
    try:
        data = request.get_json()
        email = data.get("email", "").strip()

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"message": "Invalid email address."}), 400

        if Subscriber.query.filter_by(email=email).first():
            return jsonify({"message": "You're already subscribed."}), 200

        new_subscriber = Subscriber(email=email)
        db.session.add(new_subscriber)
        db.session.commit()

        return jsonify({"message": "Thank you for subscribing!"}), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong."}), 500


# Import payment routes
from .payment_routes import *
