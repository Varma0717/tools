from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.text_summarizer_utils import summarize_text

text_summarizer_bp = Blueprint('text_summarizer', __name__, url_prefix='/tools/text-summarizer')

@text_summarizer_bp.route('/', methods=['GET'])
def text_summarizer():
    return render_template('tools/text_summarizer.html', csrf_token=generate_csrf())

@text_summarizer_bp.route('/ajax', methods=['POST'])
def text_summarizer_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        text = request.form.get('text', '')
        if not text.strip():
            return jsonify({'error': 'Please enter some text to summarize.'}), 400

        result, error = summarize_text(text)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
