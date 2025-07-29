"""
Payment Blueprint for Super SEO Toolkit
Handles payment processing and subscription management
"""

from flask import Blueprint

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")

from . import routes
