from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.writing_style_analyzer_utils import analyze_writing_style

writing_style_analyzer_bp = Blueprint('writing_style_analyzer', __name__, url_prefix='/tools/writing-style-analyzer')


@writing_style_analyzer_bp.route('/', methods=['GET'])
def writing_style_analyzer():
    return render_template('tools/writing_style_analyzer.html', csrf_token=generate_csrf())


@writing_style_analyzer_bp.route('/ajax', methods=['POST'])
def writing_style_analyzer_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))  # CSRF protection

        text = request.form.get('text', '')
        if not text.strip():
            return jsonify({'error': 'Please enter some text to analyze.'}), 400

        result, error = analyze_writing_style(text)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
