from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

social_media_preview_bp = Blueprint("social_media_preview", __name__, url_prefix="/tools")

@social_media_preview_bp.route(
    "/social-media-preview", methods=["GET", "POST"], endpoint="social_media_preview"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def social_media_preview():
    """Social Media Preview - simplified version"""
    form = URLForm()
    
    # Template uses JavaScript for interactions
    return render_template("tools/social_media_preview.html", csrf_token=generate_csrf(), form=form)
\nfrom flask import request\nfrom flask import jsonify\n\nsocial_media_preview_bp = Blueprint("social_media_preview", __name__, url_prefix="/tools")\n

@social_media_preview_bp.route("/social-media-preview/")
def social_media_preview_page():
    """Social Media Preview main page."""
    return render_template("tools/social_media_preview.html", csrf_token=generate_csrf())
