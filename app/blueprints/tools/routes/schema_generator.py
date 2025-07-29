"""
Schema Markup Generator tool for creating structured data markup.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from ..utils.schema_generator_utils import SchemaGenerator

schema_generator_bp = Blueprint("schema_generator", __name__, url_prefix="/tools")


@schema_generator_bp.route("/schema-generator/")
def schema_generator_page():
    """Schema Markup Generator main page."""
    return render_template("tools/schema_generator.html", csrf_token=generate_csrf())


@freemium_tool(limit=20, period_hours=24)
@schema_generator_bp.route("/schema-generator/generate", methods=["POST"])
def generate_schema():
    """Generate schema markup based on user input."""
    try:
        data = request.get_json()
        schema_type = data.get("schema_type", "").strip()
        schema_data = data.get("schema_data", {})

        if not schema_type:
            return jsonify({"success": False, "error": "Schema type is required"})

        generator = SchemaGenerator()
        result = generator.generate_schema(schema_type, schema_data)

        return jsonify({"success": True, "schema_type": schema_type, **result})

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Schema generation failed: {str(e)}"}
        )


@freemium_tool(limit=10, period_hours=24)
@schema_generator_bp.route("/schema-generator/validate", methods=["POST"])
def validate_schema():
    """Validate existing schema markup."""
    try:
        data = request.get_json()
        schema_markup = data.get("schema_markup", "").strip()

        if not schema_markup:
            return jsonify({"success": False, "error": "Schema markup is required"})

        generator = SchemaGenerator()
        result = generator.validate_schema(schema_markup)

        return jsonify({"success": True, **result})

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Schema validation failed: {str(e)}"}
        )


@freemium_tool(limit=15, period_hours=24)
@schema_generator_bp.route("/schema-generator/extract", methods=["POST"])
def extract_schema():
    """Extract schema markup from a webpage."""
    try:
        data = request.get_json()
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"success": False, "error": "URL is required"})

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        generator = SchemaGenerator()
        result = generator.extract_schema_from_url(url)

        return jsonify({"success": True, "url": url, **result})

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Schema extraction failed: {str(e)}"}
        )


@schema_generator_bp.route("/schema-generator/")
def schema_generator_page():
    """Schema Generator main page."""
    return render_template("tools/schema_generator.html", csrf_token=generate_csrf())
