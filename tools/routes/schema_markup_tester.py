# tools/routes/schema_markup_tester.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Optional, URL
import requests
import re
import json

schema_markup_tester_bp = Blueprint('schema_markup_tester', __name__, url_prefix='/tools')

def extract_json_ld_from_html(html):
    # Grab all <script type="application/ld+json">
    pattern = r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
    schemas = []
    for match in matches:
        schemas.append(match.strip())
    return schemas

def validate_schema(schema_code):
    try:
        json.loads(schema_code)
        return True, "Valid JSON-LD syntax."
    except Exception as e:
        return False, f"Invalid JSON-LD: {str(e)}"

@schema_markup_tester_bp.route('/schema-markup-tester', methods=['GET'])
def schema_markup_tester():
    csrf_token = generate_csrf()
    return render_template('tools/schema_markup_tester.html', csrf_token=csrf_token)

@schema_markup_tester_bp.route('/schema-markup-tester/ajax', methods=['POST'])
def schema_markup_tester_ajax():
    data = request.get_json()
    url = data.get('url', '').strip()
    code = data.get('code', '').strip()
    csrf_token = request.headers.get("X-CSRFToken", "")
    try:
        validate_csrf(csrf_token)
    except Exception:
        return jsonify({"error": "CSRF token missing or invalid."}), 400

    results = []
    if url:
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            schemas = extract_json_ld_from_html(resp.text)
            if not schemas:
                return jsonify({"warning": "No JSON-LD schema markup found on this page."})
            for s in schemas:
                valid, msg = validate_schema(s)
                results.append({"code": s, "valid": valid, "msg": msg})
            return jsonify({"results": results, "url_checked": url})
        except Exception as e:
            return jsonify({"error": f"Error fetching page: {str(e)}"}), 200
    elif code:
        valid, msg = validate_schema(code)
        results.append({"code": code, "valid": valid, "msg": msg})
        return jsonify({"results": results})
    else:
        return jsonify({"error": "Enter a URL or paste schema code."}), 400
