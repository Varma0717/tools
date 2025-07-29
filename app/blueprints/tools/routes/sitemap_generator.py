from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from app.blueprints.tools.utils.sitemap_generator_utils import generate_sitemap_xml

sitemap_generator_bp = Blueprint(
    "sitemap_generator", __name__, url_prefix="/tools/sitemap-generator"
)


@sitemap_generator_bp.route("/")
def sitemap_generator():
    return render_template("tools/sitemap_generator.html", csrf_token=generate_csrf())


@sitemap_generator_bp.route("/ajax", methods=["POST"])
def sitemap_generator_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        url = request.form.get("url", "").strip()

        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        sitemap, error = generate_sitemap_xml(url)
        if error:
            return jsonify({"error": error}), 500
        return jsonify({"sitemap": sitemap})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
\nfrom app.utils.auth_decorators import freemium_tool

@sitemap_generator_bp.route("/sitemap-generator/")
def sitemap_generator_page():
    """Sitemap Generator main page."""
    return render_template("tools/sitemap_generator.html", csrf_token=generate_csrf())
