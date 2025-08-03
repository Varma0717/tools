# tools/routes/keyword_density_analyzer.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from utils.monetization import track_tool_usage
import re
from collections import Counter


keyword_density_analyzer_bp = Blueprint(
    "keyword_density_analyzer", __name__, url_prefix="/tools"
)


# Analyze text density


def analyze_density(text):

    words = re.findall(r"\b\w+\b", text.lower())

    total = len(words)

    counter = Counter(words)

    top = counter.most_common(20)

    density = [
        {"word": w, "count": c, "density": round((c / total) * 100, 2) if total else 0}
        for w, c in top
        if len(w) > 1
    ]

    return {"total": total, "density": density}


@keyword_density_analyzer_bp.route("/keyword-density-analyzer", methods=["GET"])
@track_tool_usage
def keyword_density_analyzer():
    csrf_token = generate_csrf()
    return render_template("tools/keyword_density_analyzer.html", csrf_token=csrf_token)


@keyword_density_analyzer_bp.route("/keyword-density-analyzer/ajax", methods=["POST"])
def keyword_density_analyzer_ajax():

    data = request.get_json() or {}

    content = data.get("content", "").strip()

    csrf_token = request.headers.get("X-CSRFToken", "")

    try:

        validate_csrf(csrf_token)

    except:

        return jsonify({"error": "CSRF token missing or invalid."}), 400

    if not content:

        return jsonify({"error": "Please paste content to analyze."}), 400

    result = analyze_density(content)

    return jsonify(result)
