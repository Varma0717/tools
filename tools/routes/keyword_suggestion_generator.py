# tools/routes/keyword_suggestion_generator.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

keyword_suggestion_generator_bp = Blueprint('keyword_suggestion_generator', __name__, url_prefix='/tools')

def fetch_suggestions(seed):
    try:
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={seed}"
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        data = resp.json()
        # data[1] is the suggestion list
        if len(data) > 1 and isinstance(data[1], list):
            # Remove duplicates, limit to 20, ignore exact match
            seen = set()
            suggestions = []
            for kw in data[1]:
                if kw.lower() != seed.lower() and kw not in seen:
                    suggestions.append(kw)
                    seen.add(kw)
                if len(suggestions) >= 20:
                    break
            return suggestions
        return []
    except Exception as e:
        return {"error": str(e)}

@keyword_suggestion_generator_bp.route('/keyword-suggestion-generator', methods=['GET'])
def keyword_suggestion_generator():
    csrf_token = generate_csrf()
    return render_template('tools/keyword_suggestion_generator.html', csrf_token=csrf_token)

@keyword_suggestion_generator_bp.route('/keyword-suggestion-generator/ajax', methods=['POST'])
def keyword_suggestion_generator_ajax():
    data = request.get_json() or {}
    seed = data.get('keyword', '').strip()
    csrf_token = request.headers.get("X-CSRFToken", "")
    try:
        validate_csrf(csrf_token)
    except Exception:
        return jsonify({"error": "CSRF token missing or invalid."}), 400
    if not seed or len(seed) < 2:
        return jsonify({"error": "Enter a seed keyword."}), 400
    suggestions = fetch_suggestions(seed)
    if isinstance(suggestions, dict) and "error" in suggestions:
        return jsonify({"error": suggestions["error"]}), 200
    return jsonify({"suggestions": suggestions[:20]})
