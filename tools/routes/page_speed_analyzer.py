# tools/routes/page_speed_analyzer.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
import requests
from bs4 import BeautifulSoup
from time import time
from urllib.parse import urljoin

import traceback

csrf = CSRFProtect()

page_speed_analyzer_bp = Blueprint('page_speed_analyzer', __name__, url_prefix='/tools')

class SpeedForm(FlaskForm):
    url = StringField('Website URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Analyze Speed')

def analyze_custom_speed(url):
    from bs4 import BeautifulSoup
    import requests
    from time import time
    from urllib.parse import urljoin
    from requests.exceptions import Timeout, RequestException

    try:
        start_time = time()
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers, timeout=20)
        except Timeout:
            return {"error": f"Connection to {url} timed out."}
        except RequestException as e:
            return {"error": f"Failed to connect to {url}: {str(e)}"}

        load_time = round((time() - start_time) * 1000)
        soup = BeautifulSoup(response.text, "html.parser")
        page_size_kb = round(len(response.content) / 1024, 2)

        images = soup.find_all("img")
        scripts = soup.find_all("script")
        css_files = soup.find_all("link", rel="stylesheet")

        largest_image = {"src": "", "size_kb": 0}
        broken_resources = []
        missing_cache = []

        for tag in images + scripts + css_files:
            src = tag.get("src") or tag.get("href")
            if not src:
                continue
            full_url = urljoin(url, src)
            try:
                head_resp = requests.head(full_url, headers=headers, timeout=12, allow_redirects=True)
                if head_resp.status_code in [403, 404]:
                    broken_resources.append(full_url)

                if not head_resp.headers.get("Cache-Control"):
                    missing_cache.append(full_url)

                if tag.name == "img":
                    size = int(head_resp.headers.get("Content-Length", 0)) / 1024
                    if size > largest_image["size_kb"]:
                        largest_image = {"src": full_url, "size_kb": round(size, 2)}
            except Timeout:
                broken_resources.append(full_url + " (timeout)")
            except RequestException as e:
                broken_resources.append(full_url + f" (error: {str(e)})")

        return {
            "load_time": load_time,
            "page_size_kb": page_size_kb,
            "image_count": len(images),
            "largest_image": largest_image,
            "script_count": len(scripts),
            "css_count": len(css_files),
            "broken_resources": broken_resources,
            "missing_cache": missing_cache,
        }

    except Exception as e:
        return {"error": str(e)}

@page_speed_analyzer_bp.route('/page-speed-analyzer', methods=['GET'])
def page_speed_analyzer():
    form = SpeedForm()
    csrf_token = generate_csrf()
    return render_template("tools/page_speed_analyzer.html", form=form, csrf_token=csrf_token)

@page_speed_analyzer_bp.route('/page-speed-analyzer/ajax', methods=['POST'])
def page_speed_analyzer_ajax():
    try:
        validate_csrf(request.headers.get("X-CSRFToken"))
    except Exception:
        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"success": False, "error": "Please enter a valid URL."})

    try:
        result = analyze_custom_speed(url)
        if "error" in result:
            print("Analysis Error:", result["error"])
            return jsonify({"success": False, "error": result["error"]})
        return jsonify({"success": True, "data": result})
    except Exception as e:
        print("Unexpected Exception:", str(e))
        traceback.print_exc()  # logs full traceback to console
        return jsonify({"success": False, "error": "Unexpected error. Try again."})
