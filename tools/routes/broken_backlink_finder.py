from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect, generate_csrf
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time

csrf = CSRFProtect()

broken_backlink_finder_bp = Blueprint('broken_backlink_finder', __name__, url_prefix='/tools')

class BrokenBacklinkForm(FlaskForm):
    url = StringField('Domain or Start Page URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Find Broken Backlinks')

def is_broken(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code >= 400:
            return resp.status_code
        return False
    except Exception:
        return "ERR"

def crawl_and_find_broken_links(start_url, max_pages=40, max_broken=40):
    visited = set()
    to_visit = deque([start_url])
    broken_links = []
    parsed_start = urlparse(start_url)
    domain = parsed_start.netloc

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    page_count = 0

    while to_visit and page_count < max_pages and len(broken_links) < max_broken:
        page_url = to_visit.popleft()
        if page_url in visited:
            continue
        visited.add(page_url)
        try:
            resp = session.get(page_url, timeout=12)
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception:
            continue
        page_count += 1
        # Find and enqueue internal links
        for a in soup.find_all("a", href=True):
            href = urljoin(page_url, a['href'])
            p = urlparse(href)
            if p.netloc == domain and href.startswith(('http://', 'https://')) and href not in visited:
                # Only crawl same domain
                to_visit.append(href)

        # Find external links and check them
        for a in soup.find_all("a", href=True):
            href = urljoin(page_url, a['href'])
            p = urlparse(href)
            # Only check outbound (external) links
            if p.netloc and p.netloc != domain and href.startswith(('http://', 'https://')):
                status = is_broken(href)
                if status:
                    broken_links.append({
                        "source_page": page_url,
                        "anchor_text": a.text.strip() or "[No text]",
                        "target_url": href,
                        "status": status
                    })
                    if len(broken_links) >= max_broken:
                        break
        # Be polite (optionally sleep)
        time.sleep(0.4)
    return broken_links

@broken_backlink_finder_bp.route('/broken-backlink-finder', methods=['GET'])
def broken_backlink_finder():
    form = BrokenBacklinkForm()
    csrf_token = generate_csrf()
    return render_template('tools/broken_backlink_finder.html', form=form, csrf_token=csrf_token)

@broken_backlink_finder_bp.route('/broken-backlink-finder/ajax', methods=['POST'])
@csrf.exempt
def broken_backlink_finder_ajax():
    try:
        data = request.get_json()
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "Please enter a valid URL."}), 400
        broken_links = crawl_and_find_broken_links(url)
        if not broken_links:
            return jsonify({"broken_links": [], "message": "No broken outbound links found on crawled pages!"})
        return jsonify({"broken_links": broken_links})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("Broken backlink finder ERROR:", tb)
        return jsonify({"error": f"Internal error: {str(e)}", "details": tb}), 500
