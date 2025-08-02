from flask import Blueprint, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

csrf = CSRFProtect()

referring_domain_analyzer_bp = Blueprint('referring_domain_analyzer', __name__, url_prefix='/tools')

class RefDomainForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Analyze Referring Domains')

def get_referring_domains(target_url):
    try:
        # Uses Bing Search (public endpoint) to find inbound links
        search_url = "https://www.bing.com/search"
        params = {"q": f"linkfromdomain:{target_url}"}
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(search_url, params=params, headers=headers, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        domains = set()
        for li in soup.select("li.b_algo h2 a"):
            href = li.get('href')
            if href and href != target_url:
                parsed = urlparse(href)
                domain = f"{parsed.scheme}://{parsed.netloc}"
                domains.add(domain)
        return sorted(domains)
    except Exception as e:
        return {"error": str(e)}

@referring_domain_analyzer_bp.route('/referring-domain-analyzer', methods=['GET', 'POST'])
def referring_domain_analyzer():
    form = RefDomainForm()
    results = None
    if form.validate_on_submit():
        url = form.url.data.strip()
        results = get_referring_domains(url)
        if isinstance(results, dict) and "error" in results:
            flash(results["error"], "danger")
    return render_template('tools/referring_domain_analyzer.html', form=form, results=results)
