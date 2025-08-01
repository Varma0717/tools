"""
Security Tools Routes - Website security analysis tools
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

# Create Security tools blueprint
security_tools_bp = Blueprint("security_tools", __name__, url_prefix="/tools/security")


def is_premium_user():
    """Check if current user has premium access"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_pro_user()


@security_tools_bp.route("/")
def security_tools_index():
    """Security Tools Category Page"""
    user_has_pro = is_premium_user()

    security_tools = [
        {
            "name": "Security Headers Checker",
            "slug": "headers-checker",
            "description": "Check and validate HTTP security headers",
            "is_premium": False,
            "features": ["Header Analysis", "Security Score", "Implementation Guide"],
        },
        {
            "name": "Malware Scanner",
            "slug": "malware-scanner",
            "description": "Scan website for malware and security threats",
            "is_premium": True,
            "features": ["Malware Detection", "Threat Analysis", "Security Report"],
        },
        {
            "name": "Password Generator",
            "slug": "password-generator",
            "description": "Generate secure passwords for accounts",
            "is_premium": False,
            "features": ["Strong Passwords", "Custom Rules", "Bulk Generation"],
        },
    ]

    return render_template(
        "tools/category_index.html",
        category={
            "name": "Security Tools",
            "description": "Analyze and improve your website security",
            "tools": security_tools,
        },
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )
