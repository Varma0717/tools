from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.paraphrasing_tool_utils import paraphrase_text

paraphrasing_tool_bp = Blueprint('paraphrasing_tool', __name__, url_prefix='/tools/paraphrasing-tool')

@paraphrasing_tool_bp.route('/', methods=['GET'])
def paraphrasing_tool():
    return render_template('tools/paraphrasing_tool.html', csrf_token=generate_csrf())

@paraphrasing_tool_bp.route('/ajax', methods=['POST'])
def paraphrasing_tool_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({'error': 'Please enter text to paraphrase.'}), 400

        result, error = paraphrase_text(text)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
