from flask import Blueprint, render_template, request
from tools.forms import URLForm
from bs4 import BeautifulSoup
import requests

meta_tag_analyzer_bp = Blueprint('meta_tag_analyzer', __name__, url_prefix='/tools')

IMPORTANT_TAGS = [
    "title", "description", "keywords", "robots", "canonical",
    "og:title", "og:description", "og:image", "og:type", "og:url", "og:site_name",
    "twitter:card", "twitter:title", "twitter:description", "twitter:image",
    "viewport", "charset"
]

def get_tag_score(tag, value):
    # Simple scoring logic. You can improve!
    if not value: return 0
    if tag in ["title", "description", "og:title", "og:description", "twitter:title", "twitter:description"]:
        return 10 if len(value) >= 20 else 5
    elif tag == "canonical":
        return 10 if value.startswith("http") else 5
    elif tag == "robots":
        return 10 if "index" in value.lower() else 5
    else:
        return 10 if value else 0

@meta_tag_analyzer_bp.route('/meta-tag-analyzer', methods=['GET', 'POST'], endpoint='meta_tag_analyzer')
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
    return render_template("tools/meta_tag_analyzer.html", form=form, all_tags=all_tags, scores=scores, error=error)
