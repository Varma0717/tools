from flask import Blueprint, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

csrf = CSRFProtect()

favicon_checker_bp = Blueprint('favicon_checker', __name__, url_prefix='/tools')

class FaviconForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL(message="Enter a valid URL.")])
    submit = SubmitField('Check Favicon')

def find_favicon(url):
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, 'html.parser')
        icons = []
        for rel in ['icon', 'shortcut icon', 'apple-touch-icon', 'apple-touch-icon-precomposed']:
            for tag in soup.find_all('link', rel=rel):
                href = tag.get('href')
                if href:
                    icons.append(urljoin(url, href))
        # Default favicon fallback
        if not icons:
            # Try default /favicon.ico
            parsed = urlparse(url)
            icons.append(f"{parsed.scheme}://{parsed.netloc}/favicon.ico")
        return icons
    except Exception as e:
        return [f"Error: {e}"]

@favicon_checker_bp.route('/favicon-checker', methods=['GET', 'POST'])
def favicon_checker():
    form = FaviconForm()
    icons = None
    if form.validate_on_submit():
        url = form.url.data.strip()
        icons = find_favicon(url)
        if icons and any(i for i in icons if i.startswith("Error:")):
            flash(icons[0], "danger")
            icons = None
        elif not icons:
            flash("No favicon found.", "info")
    return render_template('tools/favicon_checker.html', form=form, icons=icons)
