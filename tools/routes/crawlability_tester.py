# tools/routes/crawlability_tester.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

csrf = CSRFProtect()
crawlability_tester_bp = Blueprint('crawlability_tester', __name__, url_prefix='/tools')

class CrawlabilityForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Test Crawlability')

def analyze_crawlability(url):
    try:
        crawl_data = {
            "robots_txt": "Not Found",
            "meta_robots": "Not Found",
            "x_robots": "Not Found",
            "http_status": "Unknown"
        }

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=8, headers=headers)
        crawl_data["http_status"] = response.status_code

        crawl_data["x_robots"] = response.headers.get("X-Robots-Tag", "None")

        soup = BeautifulSoup(response.text, 'html.parser')
        meta_robots = soup.find("meta", attrs={"name": "robots"})
        crawl_data["meta_robots"] = meta_robots['content'] if meta_robots and meta_robots.get('content') else "None"

        robots_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt"
        robots_resp = requests.get(robots_url, headers=headers, timeout=5)
        crawl_data["robots_txt"] = "Disallow found" if "disallow" in robots_resp.text.lower() else "Allow"

        results = [
            {"check": "HTTP Status Code", "status": "pass" if response.status_code == 200 else "warn", "details": str(response.status_code)},
            {"check": "X-Robots-Tag Header", "status": "fail" if "noindex" in crawl_data["x_robots"].lower() else "pass", "details": crawl_data["x_robots"]},
            {"check": "Meta Robots Tag", "status": "fail" if "noindex" in crawl_data["meta_robots"].lower() else "pass", "details": crawl_data["meta_robots"]},
            {"check": "robots.txt Rules", "status": "warn" if crawl_data["robots_txt"] == "Disallow found" else "pass", "details": crawl_data["robots_txt"]},
        ]
        return results
    except Exception as e:
        return {"error": str(e)}

@crawlability_tester_bp.route('/crawlability-tester', methods=['GET'])
def crawlability_tester():
    form = CrawlabilityForm()
    csrf_token = generate_csrf()
    return render_template('tools/crawlability_tester.html', form=form, csrf_token=csrf_token)

@crawlability_tester_bp.route('/crawlability-tester/ajax', methods=['POST'])
def crawlability_tester_ajax():
    try:
        validate_csrf(request.headers.get("X-CSRFToken"))
    except Exception:
        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "URL is required."})

    results = analyze_crawlability(url)
    if isinstance(results, dict) and "error" in results:
        return jsonify({"success": False, "error": results["error"]})
    
    return jsonify({"success": True, "results": results})
