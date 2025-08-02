from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.text_summarizer_pro_utils import summarize_text_pro

text_summarizer_pro_bp = Blueprint('text_summarizer_pro', __name__, url_prefix='/tools/text-summarizer-pro')

@text_summarizer_pro_bp.route('/', methods=['GET'])
def text_summarizer_pro():
    return render_template('tools/text_summarizer_pro.html', csrf_token=generate_csrf())

@text_summarizer_pro_bp.route('/ajax', methods=['POST'])
def text_summarizer_pro_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({'error': 'Please enter some content to summarize.'}), 400

        result, error = summarize_text_pro(text)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
