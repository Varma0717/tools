from flask import Blueprint, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect
import requests
from bs4 import BeautifulSoup

csrf = CSRFProtect()

redirect_checker_bp = Blueprint('redirect_checker', __name__, url_prefix='/tools')

class RedirectForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL(message="Enter a valid URL.")])
    submit = SubmitField('Check Redirects')

def check_redirects(url):
    chain = []
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        for r in resp.history:
            chain.append({
                'url': r.url,
                'status': r.status_code,
                'type': 'HTTP',
            })
        # Check for meta refresh at final destination
        soup = BeautifulSoup(resp.text, 'html.parser')
        meta = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta and meta.get('content'):
            chain.append({
                'url': resp.url,
                'status': resp.status_code,
                'type': 'Meta Refresh',
                'meta_content': meta['content']
            })
        else:
            chain.append({
                'url': resp.url,
                'status': resp.status_code,
                'type': 'Final',
            })
    except Exception as e:
        chain.append({'url': url, 'status': '-', 'type': f'Error: {e}'})
    return chain

@redirect_checker_bp.route('/redirect-checker', methods=['GET', 'POST'])
def redirect_checker():
    form = RedirectForm()
    chain = None
    if form.validate_on_submit():
        url = form.url.data.strip()
        chain = check_redirects(url)
        if not chain:
            flash('No redirects found or could not fetch the URL.', 'danger')
    return render_template('tools/redirect_checker.html', form=form, chain=chain)
