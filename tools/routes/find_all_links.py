from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

csrf = CSRFProtect()

find_all_links_bp = Blueprint('find_all_links', __name__, url_prefix='/tools')


class LinkFinderForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL(message="Enter a valid URL.")])
    submit = SubmitField('Find Links')


def get_links(page_url):
    try:
        resp = requests.get(page_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, 'html.parser')
        base_domain = urlparse(page_url).netloc
        internal = set()
        external = set()
        for tag in soup.find_all('a', href=True):
            href = tag['href'].strip()
            full_url = urljoin(page_url, href)
            link_domain = urlparse(full_url).netloc
            if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
                continue
            if link_domain == base_domain:
                internal.add(full_url)
            else:
                external.add(full_url)
        return {"internal": sorted(list(internal)), "external": sorted(list(external))}
    except Exception as e:
        return {"error": str(e)}


@find_all_links_bp.route('/find-all-links', methods=['GET'])
def find_all_links():
    form = LinkFinderForm()
    csrf_token = generate_csrf()
    return render_template('tools/find_all_links.html', form=form, csrf_token=csrf_token)


@find_all_links_bp.route('/find-all-links/ajax', methods=['POST'])
def find_all_links_ajax():
    try:
        validate_csrf(request.headers.get('X-CSRFToken'))
    except Exception:
        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "Please enter a valid URL."}), 400

    result = get_links(url)
    if "error" in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    return jsonify({"success": True, "result": result})
