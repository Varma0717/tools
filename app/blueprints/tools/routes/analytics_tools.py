"""
Analytics Tools Routes - Analytics and reporting tools
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

# Create Analytics tools blueprint
analytics_tools_bp = Blueprint(
    "analytics_tools", __name__, url_prefix="/tools/analytics"
)


def is_premium_user():
    """Check if current user has premium access"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_pro_user()


@analytics_tools_bp.route("/")
def analytics_tools_index():
    """Analytics Tools Category Page"""
    user_has_pro = is_premium_user()

    analytics_tools = [
        {
            "name": "Google Analytics Checker",
            "slug": "ga-checker",
            "description": "Verify Google Analytics installation and configuration",
            "is_premium": False,
            "features": [
                "Installation Check",
                "Tag Validation",
                "Configuration Review",
            ],
        },
        {
            "name": "Traffic Analyzer",
            "slug": "traffic-analyzer",
            "description": "Analyze website traffic patterns and sources",
            "is_premium": True,
            "features": ["Traffic Analysis", "Source Breakdown", "Trend Reporting"],
        },
        {
            "name": "Conversion Rate Calculator",
            "slug": "conversion-calculator",
            "description": "Calculate and optimize conversion rates",
            "is_premium": False,
            "features": ["Rate Calculation", "Goal Tracking", "Optimization Tips"],
        },
    ]

    return render_template(
        "tools/category_index.html",
        category={
            "name": "Analytics Tools",
            "description": "Analyze and track your website performance",
            "tools": analytics_tools,
        },
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )
