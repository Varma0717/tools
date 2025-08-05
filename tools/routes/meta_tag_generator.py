from flask import Blueprint, render_template, request, jsonify

from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, TextAreaField

from wtforms.validators import DataRequired, URL, Optional, Length

from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf

import requests

from bs4 import BeautifulSoup


csrf = CSRFProtect()


meta_tag_generator_bp = Blueprint("meta_tag_generator", __name__, url_prefix="/tools")


class MetaTagGenForm(FlaskForm):

    url = StringField(
        "Website URL", validators=[Optional(), URL(message="Enter a valid URL.")]
    )

    title = StringField("Page Title", validators=[Optional(), Length(max=70)])

    description = TextAreaField(
        "Meta Description", validators=[Optional(), Length(max=160)]
    )

    keywords = StringField(
        "Keywords (comma separated)", validators=[Optional(), Length(max=255)]
    )

    submit = SubmitField("Generate Meta Tags")


@meta_tag_generator_bp.route("/meta-tag-generator", methods=["GET"])
def meta_tag_generator():

    form = MetaTagGenForm()

    return render_template("tools/meta_tag_generator.html", form=form)


@meta_tag_generator_bp.route("/meta-tag-generator/ajax", methods=["POST"])
def meta_tag_generator_ajax():

    try:

        validate_csrf(request.headers.get("X-CSRFToken"))

    except Exception:

        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

    data = request.get_json()

    url = data.get("url", "").strip()

    title = data.get("title", "").strip()

    description = data.get("description", "").strip()

    keywords = data.get("keywords", "").strip()

    # If URL is present and no fields filled, attempt auto-fetch

    if url and not (title or description or keywords):

        try:

            resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})

            soup = BeautifulSoup(resp.text, "html.parser")

            title = soup.title.string.strip() if soup.title else ""

            desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
                "meta", attrs={"property": "og:description"}
            )

            description = (
                desc_tag["content"].strip()
                if desc_tag and desc_tag.get("content")
                else ""
            )

            key_tag = soup.find("meta", attrs={"name": "keywords"})

            keywords = (
                key_tag["content"].strip() if key_tag and key_tag.get("content") else ""
            )

        except Exception as e:

            return (
                jsonify(
                    {"success": False, "error": f"Failed to fetch data from URL: {e}"}
                ),
                500,
            )

    # Ensure at least one tag is provided

    if not (title or description or keywords):

        return (
            jsonify(
                {
                    "success": False,
                    "error": "Please provide at least one field or a valid URL.",
                }
            ),
            400,
        )

    tags = {"title": title, "description": description, "keywords": keywords}

    return jsonify({"success": True, "tags": tags})
