from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

domain_authority_checker_bp = Blueprint("domain_authority_checker", __name__, url_prefix="/tools")

@domain_authority_checker_bp.route(
    "/domain-authority-checker", methods=["GET", "POST"], endpoint="domain_authority_checker"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def domain_authority_checker():
    """Domain Authority Checker - simplified version"""
    form = URLForm()
    
    # Template uses JavaScript for interactions
    return render_template("tools/domain_authority_checker.html", csrf_token=generate_csrf(), form=form)
\nfrom flask import request\nfrom flask import jsonify\n\ndomain_authority_checker_bp = Blueprint("domain_authority_checker", __name__, url_prefix="/tools")\n

@domain_authority_checker_bp.route("/domain-authority-checker/")
def domain_authority_checker_page():
    """Domain Authority Checker main page."""
    return render_template("tools/domain_authority_checker.html", csrf_token=generate_csrf())
