from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.seo_content_score_calculator_utils import calculate_seo_score

seo_score_calculator_bp = Blueprint('seo_score_calculator', __name__, url_prefix='/tools/seo-content-score')

@seo_score_calculator_bp.route('/', methods=['GET'])
def seo_score_calculator():
    return render_template('tools/seo_content_score_calculator.html', csrf_token=generate_csrf())

@seo_score_calculator_bp.route('/ajax', methods=['POST'])
def seo_score_calculator_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({'error': 'Please enter content to analyze.'}), 400

        result, error = calculate_seo_score(text)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
