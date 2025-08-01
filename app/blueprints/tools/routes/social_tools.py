"""
Social Media Tools Routes - Social media optimization tools
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

# Create Social Media tools blueprint
social_tools_bp = Blueprint("social_tools", __name__, url_prefix="/tools/social")


def is_premium_user():
    """Check if current user has premium access"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_pro_user()


@social_tools_bp.route("/")
def social_tools_index():
    """Social Media Tools Category Page"""
    user_has_pro = is_premium_user()

    social_tools = [
        {
            "name": "Open Graph Preview",
            "slug": "og-preview",
            "description": "Preview how your content appears on social media",
            "is_premium": False,
            "features": ["Facebook Preview", "Twitter Preview", "LinkedIn Preview"],
        },
        {
            "name": "Social Media Hashtag Generator",
            "slug": "hashtag-generator",
            "description": "Generate relevant hashtags for social media posts",
            "is_premium": True,
            "features": [
                "Hashtag Research",
                "Trending Analysis",
                "Platform Optimization",
            ],
        },
        {
            "name": "Social Media Image Resizer",
            "slug": "image-resizer",
            "description": "Resize images for different social media platforms",
            "is_premium": False,
            "features": [
                "Multi-platform Sizing",
                "Batch Processing",
                "Template Presets",
            ],
        },
    ]

    return render_template(
        "tools/category_index.html",
        category={
            "name": "Social Media Tools",
            "description": "Optimize your content for social media platforms",
            "tools": social_tools,
        },
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )
