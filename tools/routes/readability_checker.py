from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
import re

csrf = CSRFProtect()
readability_checker_bp = Blueprint('readability_checker', __name__, url_prefix='/tools')

def count_syllables(word):
    word = word.lower()
    syllables = re.findall(r'[aeiouy]+', word)
    # Subtract silent 'e' at the end (very basic, not perfect)
    if word.endswith('e'):
        if len(syllables) > 1: syllables = syllables[:-1]
    return max(1, len(syllables))

def flesch_reading_ease(text):
    words = re.findall(r'\w+', text)
    word_count = len(words)
    sentence_count = max(1, len(re.findall(r'[.!?]', text)))
    syllable_count = sum(count_syllables(w) for w in words)
    if word_count == 0 or sentence_count == 0:
        return 0, 0, 0, 0, 0
    asl = word_count / sentence_count  # avg sentence length
    asw = syllable_count / word_count  # avg syllables per word
    flesch_score = 206.835 - (1.015 * asl) - (84.6 * asw)
    grade = (0.39 * asl) + (11.8 * asw) - 15.59
    return round(flesch_score, 1), round(grade, 1), word_count, sentence_count, syllable_count

@readability_checker_bp.route('/readability-checker', methods=['GET'])
def readability_checker():
    csrf_token = generate_csrf()
    return render_template('tools/readability_checker.html', csrf_token=csrf_token)

@readability_checker_bp.route('/readability-checker/ajax', methods=['POST'])
@csrf.exempt
def readability_checker_ajax():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text or len(text.split()) < 20:
        return jsonify({"error": "Please enter at least 20 words for accurate readability analysis."}), 400
    flesch_score, grade, words, sentences, syllables = flesch_reading_ease(text)
    grade_level = (
        "Very easy" if flesch_score >= 90 else
        "Easy" if flesch_score >= 80 else
        "Fairly easy" if flesch_score >= 70 else
        "Standard" if flesch_score >= 60 else
        "Fairly difficult" if flesch_score >= 50 else
        "Difficult" if flesch_score >= 30 else
        "Very confusing"
    )
    return jsonify({
        "flesch_score": flesch_score,
        "grade": grade,
        "grade_level": grade_level,
        "word_count": words,
        "sentence_count": sentences,
        "syllable_count": syllables
    })
