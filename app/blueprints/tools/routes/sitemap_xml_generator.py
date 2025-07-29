from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

sitemap_xml_generator_bp = Blueprint("sitemap_xml_generator", __name__, url_prefix="/tools")

@sitemap_xml_generator_bp.route(
    "/sitemap-xml-generator", methods=["GET", "POST"], endpoint="sitemap_xml_generator"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def sitemap_xml_generator():
    """Sitemap XML Generator - simplified version"""
    form = URLForm()
    
    # Template uses JavaScript for interactions
    return render_template("tools/sitemap_xml_generator.html", csrf_token=generate_csrf(), form=form)


@sitemap_xml_generator_bp.route("/sitemap-xml-generator/")
def sitemap_xml_generator_page():
    """Sitemap Xml Generator main page."""
    return render_template("tools/sitemap_xml_generator.html", csrf_token=generate_csrf())
