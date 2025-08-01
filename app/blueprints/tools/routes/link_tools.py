"""
Link Building Tools Routes - Link analysis and building tools
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

# Create Link tools blueprint
link_tools_bp = Blueprint("link_tools", __name__, url_prefix="/tools/links")


def is_premium_user():
    """Check if current user has premium access"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_pro_user()


@link_tools_bp.route("/")
def link_tools_index():
    """Link Tools Category Page"""
    user_has_pro = is_premium_user()

    link_tools = [
        {
            "name": "Backlink Quality Analyzer",
            "slug": "backlink-analyzer",
            "description": "Analyze backlink profiles and identify toxic links",
            "is_premium": True,
            "features": [
                "Backlink Analysis",
                "Toxic Link Detection",
                "Link Quality Score",
            ],
        },
        {
            "name": "Broken Link Checker",
            "slug": "broken-link-checker",
            "description": "Find and fix broken links that hurt SEO performance",
            "is_premium": False,
            "features": [
                "Link Scanning",
                "Broken Link Detection",
                "Fix Recommendations",
            ],
        },
        {
            "name": "Internal Link Analyzer",
            "slug": "internal-link-analyzer",
            "description": "Optimize internal linking structure for better SEO",
            "is_premium": True,
            "features": [
                "Link Structure",
                "Anchor Text Analysis",
                "Link Opportunities",
            ],
        },
    ]

    return render_template(
        "tools/category_index.html",
        category={
            "name": "Link Building Tools",
            "description": "Analyze and optimize your link building strategy",
            "tools": link_tools,
        },
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )
