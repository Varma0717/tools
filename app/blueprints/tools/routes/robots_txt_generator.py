from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

robots_txt_generator_bp = Blueprint("robots_txt_generator", __name__, url_prefix="/tools")

@robots_txt_generator_bp.route(
    "/robots-txt-generator", methods=["GET", "POST"], endpoint="robots_txt_generator"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def robots_txt_generator():
    """Robots.txt Generator - simplified version"""
    form = URLForm()
    
    # Template uses JavaScript for interactions
    return render_template("tools/robots_txt_generator.html", csrf_token=generate_csrf(), form=form)


@robots_txt_generator_bp.route("/robots-txt-generator/")
def robots_txt_generator_page():
    """Robots Txt Generator main page."""
    return render_template("tools/robots_txt_generator.html", csrf_token=generate_csrf())
