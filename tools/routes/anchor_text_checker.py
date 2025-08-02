from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf import FlaskForm
import requests
from bs4 import BeautifulSoup
from collections import Counter

csrf = CSRFProtect()
anchor_text_checker_bp = Blueprint('anchor_text_checker', __name__, url_prefix='/tools')

class AnchorForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Check Anchor Texts')

def get_anchor_texts(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return {"error": f"HTTP error {resp.status_code}. Site may be unreachable or protected."}
        soup = BeautifulSoup(resp.text, "html.parser")
        anchors = [a.get_text(strip=True) for a in soup.find_all("a") if a.get_text(strip=True)]
        if not anchors:
            return {"error": "No anchor texts found on this page."}
        counter = Counter(anchors)
        top_anchors = counter.most_common(25)
        return {"anchors": top_anchors}
    except Exception as e:
        return {"error": str(e)}

@anchor_text_checker_bp.route('/anchor-text-checker', methods=['GET'])
def anchor_text_checker():
    form = AnchorForm()
    csrf_token = generate_csrf()
    return render_template('tools/anchor_text_checker.html', form=form, csrf_token=csrf_token)

@anchor_text_checker_bp.route('/anchor-text-checker/ajax', methods=['POST'])
@csrf.exempt
def anchor_text_checker_ajax():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Please enter a valid URL."}), 400
    anchors = get_anchor_texts(url)
    if "error" in anchors:
        return jsonify({"error": anchors["error"]}), 400
    return jsonify({"anchors": anchors["anchors"]})
