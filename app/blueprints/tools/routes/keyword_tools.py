"""
Keyword Research Tools Routes - Keyword analysis and research tools
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

# Create Keyword tools blueprint
keyword_tools_bp = Blueprint("keyword_tools", __name__, url_prefix="/tools/keywords")


def is_premium_user():
    """Check if current user has premium access"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_pro_user()


@keyword_tools_bp.route("/")
def keyword_tools_index():
    """Keyword Tools Category Page"""
    user_has_pro = is_premium_user()

    keyword_tools = [
        {
            "name": "Keyword Difficulty Analyzer",
            "slug": "difficulty-analyzer",
            "description": "Analyze keyword competition and discover ranking opportunities",
            "is_premium": True,
            "features": [
                "Competition Analysis",
                "Difficulty Score",
                "Ranking Opportunity",
            ],
        },
        {
            "name": "Long-tail Keyword Finder",
            "slug": "longtail-finder",
            "description": "Find profitable long-tail keywords with lower competition",
            "is_premium": True,
            "features": [
                "Long-tail Discovery",
                "Search Volume",
                "Competition Analysis",
            ],
        },
        {
            "name": "Keyword Density Checker",
            "slug": "density-checker",
            "description": "Analyze keyword density and optimize content",
            "is_premium": False,
            "features": [
                "Density Analysis",
                "Keyword Distribution",
                "Optimization Tips",
            ],
        },
    ]

    return render_template(
        "tools/category_index.html",
        category={
            "name": "Keyword Research Tools",
            "description": "Research and analyze keywords for better SEO targeting",
            "tools": keyword_tools,
        },
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )
