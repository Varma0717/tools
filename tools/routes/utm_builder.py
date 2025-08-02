# tools/routes/utm_builder.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, Optional
from flask_wtf.csrf import generate_csrf, validate_csrf
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs

utm_builder_bp = Blueprint('utm_builder', __name__, url_prefix='/tools')

class UTMForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL()])
    utm_source = StringField('UTM Source', validators=[DataRequired()])
    utm_medium = StringField('UTM Medium', validators=[DataRequired()])
    utm_campaign = StringField('UTM Campaign', validators=[DataRequired()])
    utm_term = StringField('UTM Term', validators=[Optional()])
    utm_content = StringField('UTM Content', validators=[Optional()])
    submit = SubmitField('Generate UTM URL')

def build_utm_url(url, source, medium, campaign, term, content):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query['utm_source'] = [source]
    query['utm_medium'] = [medium]
    query['utm_campaign'] = [campaign]
    if term:
        query['utm_term'] = [term]
    if content:
        query['utm_content'] = [content]
    new_query = urlencode(query, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

@utm_builder_bp.route('/utm-builder', methods=['GET'])
def utm_builder():
    form = UTMForm()
    csrf_token = generate_csrf()
    return render_template("tools/utm_builder.html", form=form, csrf_token=csrf_token)

@utm_builder_bp.route('/utm-builder/ajax', methods=['POST'])
def utm_builder_ajax():
    try:
        validate_csrf(request.headers.get("X-CSRFToken"))
    except Exception:
        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

    data = request.get_json()
    try:
        utm_url = build_utm_url(
            data.get("url", ""),
            data.get("utm_source", ""),
            data.get("utm_medium", ""),
            data.get("utm_campaign", ""),
            data.get("utm_term", ""),
            data.get("utm_content", "")
        )
        return jsonify({"success": True, "utm_url": utm_url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
