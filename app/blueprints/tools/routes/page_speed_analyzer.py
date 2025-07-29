from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
import requests
import time
from bs4 import BeautifulSoup
import re

page_speed_analyzer_bp = Blueprint("page_speed_analyzer", __name__, url_prefix="/tools")


class PageSpeedForm(FlaskForm):
    url = StringField("Website URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Analyze Page Speed")


def analyze_page_speed(url):
    """Analyze page loading speed and performance metrics"""
    try:
        # Add protocol if missing
        if not url.startswith(("http:/", "https:/")):
            url = "https:/" + url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Measure loading time
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=30)
        load_time = time.time() - start_time

        response.raise_for_status()

        # Parse content
        soup = BeautifulSoup(response.content, "html.parser")

        # Basic metrics
        results = {
            "url": url,
            "status_code": response.status_code,
            "load_time": round(load_time, 2),
            "content_size": len(response.content),
            "content_size_kb": round(len(response.content) / 1024, 2),
        }

        # Count resources
        images = len(soup.find_all("img"))
        scripts = len(soup.find_all("script"))
        stylesheets = len(soup.find_all("link", rel="stylesheet"))

        results["resources"] = {
            "images": images,
            "scripts": scripts,
            "stylesheets": stylesheets,
            "total": images + scripts + stylesheets,
        }

        # Performance scoring
        score = 100
        if load_time > 3:
            score -= 30
        elif load_time > 2:
            score -= 15
        elif load_time > 1:
            score -= 5

        if results["content_size_kb"] > 1000:
            score -= 20
        elif results["content_size_kb"] > 500:
            score -= 10

        if images > 50:
            score -= 15
        elif images > 20:
            score -= 5

        results["score"] = max(0, score)

        # Performance grade
        if score >= 90:
            results["grade"] = "A"
        elif score >= 80:
            results["grade"] = "B"
        elif score >= 70:
            results["grade"] = "C"
        elif score >= 60:
            results["grade"] = "D"
        else:
            results["grade"] = "F"

        # Recommendations
        recommendations = []
        if load_time > 2:
            recommendations.append("Optimize server response time")
        if results["content_size_kb"] > 500:
            recommendations.append("Compress images and content")
        if images > 20:
            recommendations.append("Optimize number of images")
        if scripts > 10:
            recommendations.append("Minimize JavaScript files")

        results["recommendations"] = recommendations

        return results

    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}


@page_speed_analyzer_bp.route("/page-speed-analyzer/", methods=["GET"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def page_speed_analyzer():
    csrf_token = generate_csrf()
    form = PageSpeedForm()
    return render_template(
        "tools/page_speed_analyzer.html", form=form, csrf_token=csrf_token
    , csrf_token=generate_csrf())


@page_speed_analyzer_bp.route("/page-speed-analyzer/ajax", methods=["POST"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def page_speed_analyzer_ajax():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "No URL provided."}), 400

    try:
        results = analyze_page_speed(url)
        if "error" in results:
            return jsonify({"success": False, "error": results["error"]}), 400

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@page_speed_analyzer_bp.route("/page-speed-analyzer/")
def page_speed_analyzer_page():
    """Page Speed Analyzer main page."""
    return render_template("tools/page_speed_analyzer.html", csrf_token=generate_csrf())
