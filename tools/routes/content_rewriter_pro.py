from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.content_rewriter_pro_utils import rewrite_content_pro

content_rewriter_pro_bp = Blueprint('content_rewriter_pro', __name__, url_prefix='/tools/content-rewriter-pro')

@content_rewriter_pro_bp.route('/', methods=['GET'])
def content_rewriter_pro():
    return render_template('tools/content_rewriter_pro.html', csrf_token=generate_csrf())

@content_rewriter_pro_bp.route('/ajax', methods=['POST'])
def content_rewriter_pro_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({'error': 'Please enter some content to rewrite.'}), 400

        result, error = rewrite_content_pro(text)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
