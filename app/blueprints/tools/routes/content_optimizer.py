from flask import Blueprint, render_template, request, jsonify
from app.utils.auth_decorators import freemium_tool
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool

# Create blueprint
content_optimizer_bp = Blueprint("content_optimizer", __name__, url_prefix="/tools")


@content_optimizer_bp.route("/content-optimizer/")
def content_optimizer():
    """Content Optimizer tool main page."""
    return render_template("tools/content_optimizer.html", csrf_token=generate_csrf())


@freemium_tool(free_limit=15)  # 15 optimizations per day for free users
@content_optimizer_bp.route("/content-optimizer/analyze", methods=["POST"])
def analyze_content():
    """Analyze content for SEO optimization."""
    try:
        from app.blueprints.tools.utils.content_optimizer_utils import (
            analyze_content_seo,
        )

        data = request.get_json()
        content = data.get("content", "").strip()
        target_keywords = data.get("target_keywords", "").strip()
        analysis_type = data.get("analysis_type", "standard")

        if not content:
            return jsonify({"success": False, "error": "Content is required"})

        # Determine user type for analysis depth
        user_type = (
            "pro"
            if hasattr(request, "user_has_pro") and request.user_has_pro
            else "free"
        )

        results = analyze_content_seo(
            content=content,
            target_keywords=target_keywords,
            analysis_type=analysis_type,
            user_type=user_type,
        )

        return jsonify(results)

    except Exception as e:
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"})


@freemium_tool(free_limit=10)  # 10 suggestions per day for free users
@content_optimizer_bp.route("/content-optimizer/suggestions", methods=["POST"])
def get_content_suggestions():
    """Get content improvement suggestions."""
    try:
        from app.blueprints.tools.utils.content_optimizer_utils import (
            get_improvement_suggestions,
        )

        data = request.get_json()
        content = data.get("content", "").strip()
        target_keywords = data.get("target_keywords", "").strip()
        content_type = data.get("content_type", "blog")

        if not content:
            return jsonify({"success": False, "error": "Content is required"})

        user_type = (
            "pro"
            if hasattr(request, "user_has_pro") and request.user_has_pro
            else "free"
        )

        suggestions = get_improvement_suggestions(
            content=content,
            target_keywords=target_keywords,
            content_type=content_type,
            user_type=user_type,
        )

        return jsonify(suggestions)

    except Exception as e:
        return jsonify({"success": False, "error": f"Suggestions failed: {str(e)}"})


@freemium_tool(free_limit=20)  # 20 readability checks per day for free users
@content_optimizer_bp.route("/content-optimizer/readability", methods=["POST"])
def check_readability():
    """Check content readability score."""
    try:
        from app.blueprints.tools.utils.content_optimizer_utils import (
            analyze_readability,
        )

        data = request.get_json()
        content = data.get("content", "").strip()

        if not content:
            return jsonify({"success": False, "error": "Content is required"})

        user_type = (
            "pro"
            if hasattr(request, "user_has_pro") and request.user_has_pro
            else "free"
        )

        readability_results = analyze_readability(content, user_type)

        return jsonify(readability_results)

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Readability analysis failed: {str(e)}"}
        )


@content_optimizer_bp.route("/content-optimizer/")
def content_optimizer_page():
    """Content Optimizer main page."""
    return render_template("tools/content_optimizer.html", csrf_token=generate_csrf())
