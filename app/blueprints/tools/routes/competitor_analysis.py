from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

competitor_analysis_bp = Blueprint("competitor_analysis", __name__, url_prefix="/tools")

@competitor_analysis_bp.route(
    "/competitor-analysis", methods=["GET", "POST"], endpoint="competitor_analysis"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def competitor_analysis():
    """Competitor Analysis - simplified version"""
    form = URLForm()
    
    # Template uses JavaScript for interactions
    return render_template("tools/competitor_analysis.html", csrf_token=generate_csrf(), form=form)
\nfrom flask import request\nfrom flask import jsonify\n\ncompetitor_analysis_bp = Blueprint("competitor_analysis", __name__, url_prefix="/tools")\n

@competitor_analysis_bp.route("/competitor-analysis/")
def competitor_analysis_page():
    """Competitor Analysis main page."""
    return render_template("tools/competitor_analysis.html", csrf_token=generate_csrf())
