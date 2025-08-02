from flask import Blueprint, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect
import requests
from bs4 import BeautifulSoup

csrf = CSRFProtect()

hreflang_tag_checker_bp = Blueprint('hreflang_tag_checker', __name__, url_prefix='/tools')

class HreflangForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL(message="Enter a valid URL.")])
    submit = SubmitField('Check Hreflang Tags')

@hreflang_tag_checker_bp.route('/hreflang-tag-checker', methods=['GET', 'POST'])
def hreflang_tag_checker():
    form = HreflangForm()
    hreflangs = None
    if form.validate_on_submit():
        url = form.url.data.strip()
        try:
            resp = requests.get(url, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, 'html.parser')
            hreflang_tags = soup.find_all('link', rel='alternate')
            hreflangs = []
            for tag in hreflang_tags:
                hreflang = tag.get('hreflang')
                href = tag.get('href')
                if hreflang and href:
                    hreflangs.append({'hreflang': hreflang, 'href': href})
            if not hreflangs:
                flash('No hreflang tags found on this page.', 'info')
        except Exception as e:
            flash(f"Failed to fetch hreflang tags: {e}", "danger")
    return render_template('tools/hreflang_tag_checker.html', form=form, hreflangs=hreflangs)
