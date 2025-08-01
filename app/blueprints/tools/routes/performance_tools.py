"""
Performance Tools Routes - Speed and performance optimization tools
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

# Create Performance tools blueprint
performance_tools_bp = Blueprint(
    "performance_tools", __name__, url_prefix="/tools/performance"
)


def is_premium_user():
    """Check if current user has premium access"""
    if not current_user.is_authenticated:
        return False
    return current_user.is_pro_user()


@performance_tools_bp.route("/")
def performance_tools_index():
    """Performance Tools Category Page"""
    user_has_pro = is_premium_user()

    performance_tools = [
        {
            "name": "Site Speed Analyzer",
            "slug": "speed-analyzer",
            "description": "Advanced Core Web Vitals and performance analysis",
            "is_premium": True,
            "features": ["Core Web Vitals", "Performance Score", "Optimization Tips"],
        },
        {
            "name": "Image Optimizer",
            "slug": "image-optimizer",
            "description": "Compress and optimize images for better performance",
            "is_premium": False,
            "features": ["Image Compression", "Format Conversion", "Bulk Processing"],
        },
        {
            "name": "CSS/JS Minifier",
            "slug": "minifier",
            "description": "Minify CSS and JavaScript files for faster loading",
            "is_premium": False,
            "features": ["CSS Minification", "JS Minification", "Code Optimization"],
        },
    ]

    return render_template(
        "tools/category_index.html",
        category={
            "name": "Performance Tools",
            "description": "Optimize your website speed and performance",
            "tools": performance_tools,
        },
        user_has_pro=user_has_pro,
        user_is_authenticated=current_user.is_authenticated,
    )
