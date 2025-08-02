from flask import Blueprint, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect
import requests
from bs4 import BeautifulSoup

csrf = CSRFProtect()

canonical_tag_checker_bp = Blueprint('canonical_tag_checker', __name__, url_prefix='/tools')

class CanonicalForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL(message="Enter a valid URL.")])
    submit = SubmitField('Check Canonical Tag')

@canonical_tag_checker_bp.route('/canonical-tag-checker', methods=['GET', 'POST'])
def canonical_tag_checker():
    form = CanonicalForm()
    canonical = None
    if form.validate_on_submit():
        url = form.url.data.strip()
        try:
            resp = requests.get(url, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, 'html.parser')
            tag = soup.find('link', rel='canonical')
            if tag and tag.get('href'):
                canonical = tag['href']
            else:
                flash('No canonical tag found on this page.', 'info')
        except Exception as e:
            flash(f"Failed to fetch canonical tag: {e}", "danger")
    return render_template('tools/canonical_tag_checker.html', form=form, canonical=canonical)
