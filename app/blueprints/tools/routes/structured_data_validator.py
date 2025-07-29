from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

structured_data_validator_bp = Blueprint("structured_data_validator", __name__, url_prefix="/tools")

@structured_data_validator_bp.route(
    "/structured-data-validator", methods=["GET", "POST"], endpoint="structured_data_validator"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def structured_data_validator():
    """Structured Data Validator - simplified version"""
    form = URLForm()
    
    # Template uses JavaScript for interactions
    return render_template("tools/structured_data_validator.html", csrf_token=generate_csrf(), form=form)
\nfrom flask import request\nfrom flask import jsonify\n\nstructured_data_validator_bp = Blueprint("structured_data_validator", __name__, url_prefix="/tools")\n

@structured_data_validator_bp.route("/structured-data-validator/")
def structured_data_validator_page():
    """Structured Data Validator main page."""
    return render_template("tools/structured_data_validator.html", csrf_token=generate_csrf())
