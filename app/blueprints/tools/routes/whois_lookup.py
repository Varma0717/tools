from flask import Blueprint, render_template, request
from app.blueprints.tools.forms import URLForm
from app.utils.auth_decorators import freemium_tool

whois_lookup_bp = Blueprint("whois_lookup", __name__, url_prefix="/tools")

@whois_lookup_bp.route(
    "/whois-lookup", methods=["GET", "POST"], endpoint="whois_lookup"
)
@freemium_tool(requires_login=False, is_premium=False, free_limit=10)
def whois_lookup():
    """WHOIS Lookup tool - simplified version"""
    form = URLForm()
    results, error = None, None
    
    if form.validate_on_submit():
        url = form.url.data.strip()
        if not url.startswith("http"):
            url = "https://" + url
        
        try:
            # Placeholder for tool logic
            results = {
                "url": url,
                "status": "analyzed",
                "message": "Analysis complete. This is a demo version of the WHOIS Lookup."
            }
        except Exception as e:
            error = f"Error during analysis: {str(e)}"
    
    return render_template(
        "tools/whois_lookup.html",
        form=form,
        results=results,
        error=error,
    )
\nfrom flask import jsonify\nfrom flask_wtf.csrf import generate_csrf\n\nwhois_lookup_bp = Blueprint("whois_lookup", __name__, url_prefix="/tools")\n

@whois_lookup_bp.route("/whois-lookup/")
def whois_lookup_page():
    """Whois Lookup main page."""
    return render_template("tools/whois_lookup.html", csrf_token=generate_csrf())
