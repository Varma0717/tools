from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect, generate_csrf
from app.utils.auth_decorators import freemium_tool
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

csrf = CSRFProtect()

meta_tag_analyzer_bp = Blueprint("meta_tag_analyzer", __name__, url_prefix="/tools")


class MetaTagForm(FlaskForm):
    url = StringField("Website URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Analyze Meta Tags")


def analyze_meta_tags(url):
    """Analyze meta tags of a given URL"""
    try:
        # Add protocol if missing
        if not url.startswith(("http:/", "https:/")):
            url = "https:/" + url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        results = {}

        # Title tag
        title_tag = soup.find("title")
        results["title"] = title_tag.get_text().strip() if title_tag else None

        # Meta description
        description_tag = soup.find("meta", attrs={"name": "description"})
        results["description"] = (
            description_tag.get("content", "").strip() if description_tag else None
        )

        # Meta keywords
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        results["keywords"] = (
            keywords_tag.get("content", "").strip() if keywords_tag else None
        )

        # Canonical URL
        canonical_tag = soup.find("link", attrs={"rel": "canonical"})
        results["canonical"] = (
            canonical_tag.get("href", "").strip() if canonical_tag else None
        )

        # Robots meta
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        results["robots"] = (
            robots_tag.get("content", "").strip() if robots_tag else None
        )

        # Open Graph tags
        og_tags = {}
        for og_tag in soup.find_all("meta", property=re.compile(r"^og:")):
            property_name = og_tag.get("property", "")
            content = og_tag.get("content", "")
            if property_name and content:
                og_tags[property_name] = content
        results["open_graph"] = og_tags

        # Twitter Card tags
        twitter_tags = {}
        for twitter_tag in soup.find_all(
            "meta", attrs={"name": re.compile(r"^twitter:")}
        ):
            name = twitter_tag.get("name", "")
            content = twitter_tag.get("content", "")
            if name and content:
                twitter_tags[name] = content
        results["twitter"] = twitter_tags

        # All meta tags
        all_meta = []
        for meta in soup.find_all("meta"):
            meta_info = {}
            if meta.get("name"):
                meta_info["type"] = "name"
                meta_info["attribute"] = meta.get("name")
            elif meta.get("property"):
                meta_info["type"] = "property"
                meta_info["attribute"] = meta.get("property")
            elif meta.get("http-equiv"):
                meta_info["type"] = "http-equiv"
                meta_info["attribute"] = meta.get("http-equiv")
            else:
                continue

            meta_info["content"] = meta.get("content", "")
            if meta_info["content"]:
                all_meta.append(meta_info)

        results["all_meta"] = all_meta
        results["url"] = url
        results["status_code"] = response.status_code

        return results

    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}


@meta_tag_analyzer_bp.route("/meta-tag-analyzer/", methods=["GET"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def meta_tag_analyzer():
    csrf_token = generate_csrf()
    form = MetaTagForm()
    return render_template(
        "tools/meta_tag_analyzer.html", form=form, csrf_token=csrf_token
    , csrf_token=generate_csrf())


@meta_tag_analyzer_bp.route("/meta-tag-analyzer/ajax", methods=["POST"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def meta_tag_analyzer_ajax():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "No URL provided."}), 400

    try:
        results = analyze_meta_tags(url)
        if "error" in results:
            return jsonify({"success": False, "error": results["error"]}), 400

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@meta_tag_analyzer_bp.route("/meta-tag-analyzer/")
def meta_tag_analyzer_page():
    """Meta Tag Analyzer main page."""
    return render_template("tools/meta_tag_analyzer.html", csrf_token=generate_csrf())
