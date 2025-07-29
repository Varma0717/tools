from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

local_seo_analyzer_bp = Blueprint("local_seo_analyzer", __name__, url_prefix="/tools")

@local_seo_analyzer_bp.route(
    "/local-seo-analyzer", methods=["GET", "POST"], endpoint="local_seo_analyzer"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def local_seo_analyzer():
    """Local SEO Analyzer - simplified version"""
    form = URLForm()
    
    # Template uses JavaScript for interactions
    return render_template("tools/local_seo_analyzer.html", csrf_token=generate_csrf(), form=form)
\nfrom flask import request\nfrom flask import jsonify\n\nlocal_seo_analyzer_bp = Blueprint("local_seo_analyzer", __name__, url_prefix="/tools")\n

@local_seo_analyzer_bp.route("/local-seo-analyzer/")
def local_seo_analyzer_page():
    """Local Seo Analyzer main page."""
    return render_template("tools/local_seo_analyzer.html", csrf_token=generate_csrf())
