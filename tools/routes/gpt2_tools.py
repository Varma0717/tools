from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError
from tools.utils.gpt2_utils import gpt2_generator

gpt2_tools_bp = Blueprint('gpt2_tools', __name__, url_prefix='/tools/gpt2')

@gpt2_tools_bp.route('/')
def index():
    return render_template('tools/gpt2_index.html')

@gpt2_tools_bp.route('/generate', methods=['POST'])
def generate():
    try:
        csrf_token = request.headers.get('X-CSRFToken') or request.json.get('csrf_token')
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({"error": "Please provide input text"}), 400

    try:
        generated_text = gpt2_generator.generate(prompt, max_length=200)
        return jsonify({"result": generated_text})
    except Exception as e:
        return jsonify({"error": "Generation error: " + str(e)}), 500
