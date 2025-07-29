from flask_wtf.csrf import generate_csrf\n"""
Website Speed Tester tool for analyzing page load performance and Core Web Vitals.
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.decorators import freemium_tool
from .utils.speed_tester_utils import SpeedTester

speed_tester_bp = Blueprint("speed_tester", __name__, url_prefix="/tools")


@speed_tester_bp.route("/speed-tester/")
def speed_tester_page():
    """Website Speed Tester main page."""
    return render_template("tools/speed_tester.html")


@freemium_tool(limit=10, period_hours=24)
@speed_tester_bp.route("/speed-tester/analyze", methods=["POST"])
def analyze_speed():
    """Analyze website speed and Core Web Vitals."""
    try:
        data = request.get_json()
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"success": False, "error": "URL is required"})

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        speed_tester = SpeedTester()
        results = speed_tester.analyze_speed(url)

        return jsonify({"success": True, "url": url, **results})

    except Exception as e:
        return jsonify({"success": False, "error": f"Speed analysis failed: {str(e)}"})


@freemium_tool(limit=5, period_hours=24)
@speed_tester_bp.route("/speed-tester/core-web-vitals", methods=["POST"])
def analyze_core_web_vitals():
    """Analyze Core Web Vitals specifically."""
    try:
        data = request.get_json()
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"success": False, "error": "URL is required"})

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        speed_tester = SpeedTester()
        results = speed_tester.analyze_core_web_vitals(url)

        return jsonify({"success": True, "url": url, **results})

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Core Web Vitals analysis failed: {str(e)}"}
        )


@freemium_tool(limit=15, period_hours=24)
@speed_tester_bp.route("/speed-tester/performance-insights", methods=["POST"])
def get_performance_insights():
    """Get detailed performance insights and optimization suggestions."""
    try:
        data = request.get_json()
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"success": False, "error": "URL is required"})

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        speed_tester = SpeedTester()
        results = speed_tester.get_performance_insights(url)

        return jsonify({"success": True, "url": url, **results})

    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Performance insights failed: {str(e)}"}
        )


@speed_tester_bp.route("/speed-tester/")
def speed_tester_page():
    """Speed Tester main page."""
    return render_template("tools/speed_tester.html", csrf_token=generate_csrf())
