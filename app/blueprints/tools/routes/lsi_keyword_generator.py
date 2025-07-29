from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf

from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField

from wtforms.validators import DataRequired

from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf

import requests

import re


csrf = CSRFProtect()


lsi_keyword_generator_bp = Blueprint(
    "lsi_keyword_generator", __name__, url_prefix="/tools"
)


class LSIForm(FlaskForm):

    keyword = StringField("Seed Keyword", validators=[DataRequired()])

    submit = SubmitField("Generate LSI Keywords")


def fetch_lsi_keywords(seed):

    try:

        url = f"https://www.google.com/search?q={seed}&hl=en"

        headers = {"User-Agent": "Mozilla/5.0"}

        resp = requests.get(url, headers=headers, timeout=10)

        matches = re.findall(r'<a[^>]+href="/search\?q=([^"&]+)&amp;', resp.text)

        lsi_terms = []

        for match in matches:

            term = match.replace("+", " ")

            if seed.lower() not in term.lower() and len(term.split()) > 1:

                lsi_terms.append(term)

        lsi_terms = list(dict.fromkeys(lsi_terms))[:15]

        return lsi_terms

    except Exception as e:

        return {"error": str(e)}


@lsi_keyword_generator_bp.route("/lsi-keyword-generator", methods=["GET"])
def lsi_keyword_generator():

    form = LSIForm()

    csrf_token = generate_csrf()

    return render_template(
        "tools/lsi_keyword_generator.html", form=form, csrf_token=csrf_token
    )


@lsi_keyword_generator_bp.route("/lsi-keyword-generator/ajax", methods=["POST"])
def lsi_keyword_generator_ajax():

    try:

        validate_csrf(request.headers.get("X-CSRFToken"))

    except Exception:

        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

    data = request.get_json()

    keyword = data.get("keyword", "").strip()

    if not keyword:

        return jsonify({"success": False, "error": "Please enter a seed keyword."})

    result = fetch_lsi_keywords(keyword)

    if isinstance(result, dict) and "error" in result:

        return jsonify({"success": False, "error": result["error"]})

    return jsonify({"success": True, "keywords": result})
\nfrom app.utils.auth_decorators import freemium_tool\n\nlsi_keyword_generator_bp = Blueprint("lsi_keyword_generator", __name__, url_prefix="/tools")\n

@lsi_keyword_generator_bp.route("/lsi-keyword-generator/")
def lsi_keyword_generator_page():
    """Lsi Keyword Generator main page."""
    return render_template("tools/lsi_keyword_generator.html", csrf_token=generate_csrf())
