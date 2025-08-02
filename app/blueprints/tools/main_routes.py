"""
Tools blueprint - Coming Soon functionality only
"""

from flask import Blueprint, render_template

tools_bp = Blueprint("tools", __name__, url_prefix="/tools")


@tools_bp.route("/")
def tools_home():
    """Tools home page - coming soon."""
    return render_template("tools/coming_soon.html", title="SEO Tools - Coming Soon")


@tools_bp.route("/<tool_name>")
def tool_coming_soon(tool_name):
    """Individual tool coming soon page."""
    return render_template(
        "tools/coming_soon.html",
        title=f"{tool_name.replace('-', ' ').title()} - Coming Soon",
        tool_name=tool_name,
    )
