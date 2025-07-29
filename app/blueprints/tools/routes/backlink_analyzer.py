from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

backlink_analyzer_bp = Blueprint("backlink_analyzer", __name__, url_prefix="/tools")

@backlink_analyzer_bp.route(
    "/backlink-analyzer", methods=["GET", "POST"], endpoint="backlink_analyzer"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def backlink_analyzer():
    """Backlink Analyzer - simplified version"""
    form = URLForm()
    
    # Template uses JavaScript for interactions
    return render_template("tools/backlink_analyzer.html", csrf_token=generate_csrf(), form=form)
\nfrom flask import request\nfrom flask import jsonify\n\nbacklink_analyzer_bp = Blueprint("backlink_analyzer", __name__, url_prefix="/tools")\n

@backlink_analyzer_bp.route("/backlink-analyzer/")
def backlink_analyzer_page():
    """Backlink Analyzer main page."""
    return render_template("tools/backlink_analyzer.html", csrf_token=generate_csrf())
