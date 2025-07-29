from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import string

keyword_density_analyzer_bp = Blueprint(
    "keyword_density_analyzer", __name__, url_prefix="/tools"
)


class KeywordForm(FlaskForm):
    url = StringField("Website URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Analyze Keywords")


def analyze_keyword_density(url):
    """Analyze keyword density of a webpage"""
    try:
        if not url.startswith(("http:/", "https:/")):
            url = "https:/" + url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean and process text
        text = re.sub(r"\s+", " ", text)
        text = text.lower()

        # Remove punctuation and split into words
        translator = str.maketrans("", "", string.punctuation)
        words = text.translate(translator).split()

        # Filter out short words and common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
        }
        filtered_words = [
            word for word in words if len(word) > 2 and word not in stop_words
        ]

        # Count words
        word_count = Counter(filtered_words)
        total_words = len(filtered_words)

        # Calculate density for top words
        top_keywords = []
        for word, count in word_count.most_common(20):
            density = (count / total_words) * 100
            top_keywords.append(
                {"keyword": word, "count": count, "density": round(density, 2)}
            )

        # Get 2-gram phrases
        bigrams = []
        for i in range(len(filtered_words) - 1):
            bigram = f"{filtered_words[i]} {filtered_words[i+1]}"
            bigrams.append(bigram)

        bigram_count = Counter(bigrams)
        top_bigrams = []
        for phrase, count in bigram_count.most_common(10):
            if count > 1:  # Only show phrases that appear more than once
                density = (count / len(bigrams)) * 100
                top_bigrams.append(
                    {"phrase": phrase, "count": count, "density": round(density, 2)}
                )

        results = {
            "url": url,
            "total_words": total_words,
            "unique_words": len(word_count),
            "top_keywords": top_keywords,
            "top_phrases": top_bigrams,
        }

        return results

    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}


@keyword_density_analyzer_bp.route("/keyword-density-analyzer/", methods=["GET"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def keyword_density_analyzer():
    csrf_token = generate_csrf()
    form = KeywordForm()
    return render_template(
        "tools/keyword_density_analyzer.html", form=form, csrf_token=csrf_token
    , csrf_token=generate_csrf())


@keyword_density_analyzer_bp.route("/keyword-density-analyzer/ajax", methods=["POST"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def keyword_density_analyzer_ajax():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "No URL provided."}), 400

    try:
        results = analyze_keyword_density(url)
        if "error" in results:
            return jsonify({"success": False, "error": results["error"]}), 400

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@keyword_density_analyzer_bp.route("/keyword-density-analyzer/")
def keyword_density_analyzer_page():
    """Keyword Density Analyzer main page."""
    return render_template("tools/keyword_density_analyzer.html", csrf_token=generate_csrf())
