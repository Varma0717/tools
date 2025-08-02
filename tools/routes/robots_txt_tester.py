# tools/routes/robots_txt_tester.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Optional, URL
import requests

robots_txt_tester_bp = Blueprint('robots_txt_tester', __name__, url_prefix='/tools')

def parse_robots(robots_txt, user_agent, path):
    from urllib import robotparser
    rp = robotparser.RobotFileParser()
    try:
        rp.parse(robots_txt.splitlines())
        allowed = rp.can_fetch(user_agent, path)
        return allowed
    except Exception:
        return None

@robots_txt_tester_bp.route('/robots-txt-tester', methods=['GET'])
def robots_txt_tester():
    csrf_token = generate_csrf()
    return render_template('tools/robots_txt_tester.html', csrf_token=csrf_token)

@robots_txt_tester_bp.route('/robots-txt-tester/ajax', methods=['POST'])
def robots_txt_tester_ajax():
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    robots_txt = data.get('robots_txt', '').strip()
    test_path = data.get('test_path', '').strip() or "/"
    user_agent = data.get('user_agent', '').strip() or "*"
    csrf_token = request.headers.get("X-CSRFToken", "")

    try:
        validate_csrf(csrf_token)
    except Exception:
        return jsonify({"error": "CSRF token missing or invalid."}), 400

    fetched_txt = ""
    result = None
    generated = None

    try:
        # 1. If robots.txt provided, use it
        if robots_txt:
            fetched_txt = robots_txt
        # 2. If URL provided, try to fetch robots.txt
        elif url:
            try:
                r = requests.get(url.rstrip('/') + '/robots.txt', timeout=7, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200 and r.text.strip():
                    fetched_txt = r.text
                else:
                    return jsonify({"error": "robots.txt not found or is empty on this URL."}), 200
            except Exception as e:
                return jsonify({"error": f"Failed to fetch robots.txt: {e}"}), 200

        # 3. If robots.txt present, test it
        if fetched_txt and test_path:
            try:
                allowed = parse_robots(fetched_txt, user_agent, test_path)
                if allowed is None:
                    result = "Could not parse robots.txt or invalid test path."
                else:
                    result = f"Allowed: {allowed} (for user-agent '{user_agent}' on path '{test_path}')"
                return jsonify({"result": result, "fetched_txt": fetched_txt})
            except Exception as e:
                return jsonify({"error": f"Error parsing robots.txt: {e}"}), 200
        # 4. If nothing provided, generate template
        elif not fetched_txt and not url:
            generated = (
                "User-agent: *\n"
                "Disallow: /wp-admin/\n"
                "Allow: /wp-admin/admin-ajax.php\n"
                "Sitemap: https://yourdomain.com/sitemap.xml"
            )
            return jsonify({"generated": generated})
        else:
            return jsonify({"error": "Please provide a website URL or robots.txt content."}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 200
