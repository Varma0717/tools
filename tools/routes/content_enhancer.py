from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.content_enhancer_utils import enhance_content

content_enhancer_bp = Blueprint('content_enhancer', __name__, url_prefix='/tools/content-enhancer')

@content_enhancer_bp.route('/', methods=['GET'])
def content_enhancer():
    return render_template('tools/content_enhancer.html', csrf_token=generate_csrf())

@content_enhancer_bp.route('/ajax', methods=['POST'])
def content_enhancer_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({'error': 'Please enter content to enhance.'}), 400

        result, error = enhance_content(text)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
