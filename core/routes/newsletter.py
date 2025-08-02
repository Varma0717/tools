# core/routes/newsletter.py

from flask import Blueprint, request, jsonify
from models import db, NewsletterSubscriber

newsletter_bp = Blueprint('newsletter', __name__)

@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')

    if not email or "@" not in email:
        return jsonify({ "success": False, "message": "Invalid email." })

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        return jsonify({ "success": False, "message": "Already subscribed." })

    new_subscriber = NewsletterSubscriber(email=email)
    db.session.add(new_subscriber)
    db.session.commit()

    return jsonify({ "success": True, "message": "Subscribed successfully!" })
