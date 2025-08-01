"""
Technical SEO Tools Routes - Technical SEO analysis and optimization
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

# Create Technical SEO tools blueprint
technical_tools_bp = Blueprint(
    "technical_tools", __name__, url_prefix="/tools/technical"
)


def is_premium_user():
    """Check if current user has premium access"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_pro_user()


@technical_tools_bp.route("/")
def technical_tools_index():
    """Technical SEO Tools Category Page"""
    user_has_pro = is_premium_user()

    technical_tools = [
        {
            "name": "Schema Markup Validator",
            "slug": "schema-validator",
            "description": "Validate and optimize structured data markup",
            "is_premium": False,
            "features": [
                "Schema Validation",
                "Markup Testing",
                "Rich Snippets Preview",
            ],
        },
        {
            "name": "Robots.txt Generator",
            "slug": "robots-generator",
            "description": "Generate and validate robots.txt files",
            "is_premium": False,
            "features": [
                "Robots.txt Generation",
                "Syntax Validation",
                "Best Practices",
            ],
        },
        {
            "name": "SSL Certificate Checker",
            "slug": "ssl-checker",
            "description": "Check SSL certificate status and security",
            "is_premium": False,
            "features": ["SSL Validation", "Certificate Details", "Security Analysis"],
        },
    ]

    return render_template(
        "tools/category_index.html",
        category={
            "name": "Technical SEO Tools",
            "description": "Technical SEO analysis and optimization tools",
            "tools": technical_tools,
        },
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )
