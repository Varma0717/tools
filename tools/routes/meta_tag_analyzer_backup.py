from flask import Blueprint, render_template, request, jsonify
from utils.professional_decorators import login_required_infrastructure
from tools.forms import URLForm
from bs4 import BeautifulSoup
import requests
from datetime import datetime

meta_tag_analyzer_bp = Blueprint("meta_tag_analyzer", __name__, url_prefix="/tools")

IMPORTANT_TAGS = [
    "title",
    "description",
    "keywords",
    "robots",
    "canonical",
    "og:title",
    "og:description",
    "og:image",
    "og:type",
    "og:url",
    "og:site_name",
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
    "viewport",
    "charset",
    "author",
    "generator",
    "rating",
]


def get_tag_score(tag, value):
    """Professional scoring algorithm for meta tags"""
    if not value:
        return {
            "score": 0,
            "status": "missing",
            "recommendation": f"{tag} tag is missing",
        }

    score = 0
    status = "good"
    recommendation = f"{tag} tag is properly configured"

    if tag in ["title", "og:title", "twitter:title"]:
        length = len(value)
        if 50 <= length <= 60:
            score = 100
        elif 30 <= length <= 70:
            score = 80
        elif length < 30:
            score = 40
            status = "warning"
            recommendation = f"{tag} is too short (recommended: 50-60 characters)"
        else:
            score = 60
            status = "warning"
            recommendation = f"{tag} is too long (recommended: 50-60 characters)"

    elif tag in ["description", "og:description", "twitter:description"]:
        length = len(value)
        if 150 <= length <= 160:
            score = 100
        elif 120 <= length <= 180:
            score = 80
        elif length < 120:
            score = 50
            status = "warning"
            recommendation = f"{tag} is too short (recommended: 150-160 characters)"
        else:
            score = 60
            status = "warning"
            recommendation = f"{tag} is too long (recommended: 150-160 characters)"

    elif tag == "canonical":
        if value.startswith(("http://", "https://")):
            score = 100
        else:
            score = 40
            status = "error"
            recommendation = "Canonical URL should be absolute"

    elif tag == "robots":
        if any(directive in value.lower() for directive in ["index", "follow"]):
            score = 100
        elif "noindex" in value.lower():
            score = 80
            status = "warning"
            recommendation = "Page is set to noindex"
        else:
            score = 60

    else:
        score = 90 if value else 0

    return {
        "score": score,
        "status": status,
        "recommendation": recommendation,
        "length": len(value) if value else 0,
    }


@meta_tag_analyzer_bp.route(
    "/meta-tag-analyzer", methods=["GET", "POST"], endpoint="meta_tag_analyzer"
)
def meta_tag_analyzer():

    form = URLForm()

    all_tags, scores, error = [], {}, None

    if form.validate_on_submit():

        url = form.url.data.strip()

        if not url.startswith("http"):

            url = "https://" + url

        try:

            headers = {"User-Agent": "Mozilla/5.0"}

            resp = requests.get(url, headers=headers, timeout=12)

            soup = BeautifulSoup(resp.text, "html.parser")

            # --- Get <title> ---

            title = soup.title.string.strip() if soup.title else ""

            if title:

                all_tags.append({"name": "title", "value": title})

            # --- Get all <meta ...> tags ---

            for tag in soup.find_all("meta"):

                name = tag.get("name") or tag.get("property") or tag.get("http-equiv")

                content = tag.get("content") or tag.get("value") or ""

                charset = tag.get("charset")

                if name and content:

                    all_tags.append({"name": name, "value": content})

                elif charset:

                    all_tags.append({"name": "charset", "value": charset})

            # --- Get canonical link ---

            canonical = soup.find("link", rel="canonical")

            if canonical and canonical.get("href"):

                all_tags.append({"name": "canonical", "value": canonical.get("href")})

            # --- Get other <link rel="..."> tags (amphtml, alternate, etc.) ---

            for link in soup.find_all("link"):

                rel = link.get("rel")

                if rel and link.get("href"):

                    rel = " ".join(rel) if isinstance(rel, list) else rel

                    all_tags.append({"name": f"link:{rel}", "value": link.get("href")})

            # --- De-duplicate by name ---

            deduped = {}

            for t in all_tags:

                if t["name"] not in deduped:

                    deduped[t["name"]] = t["value"]

            all_tags = [{"name": k, "value": v} for k, v in deduped.items()]

            # --- Score important tags ---

            for t in all_tags:

                tag = t["name"].lower()

                if tag in IMPORTANT_TAGS:

                    scores[tag] = get_tag_score(tag, t["value"])

        except Exception as e:

            error = f"Error analyzing tags: {str(e)}"

    return render_template(
        "tools/meta_tag_analyzer.html",
        form=form,
        all_tags=all_tags,
        scores=scores,
        error=error,
    )
