from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError
from tools.utils.gptneo_utils import gptneo_generator

gptneo_tools_bp = Blueprint('gptneo_tools', __name__, url_prefix='/tools/gptneo')

@gptneo_tools_bp.route('/')
def gptneo():
    return render_template('tools/gptneo_index.html')

@gptneo_tools_bp.route('/generate', methods=['POST'])
def gptneo_generate():
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
        generated_text = gptneo_generator.generate(prompt, max_length=250)
        return jsonify({"result": generated_text})
    except Exception as e:
        return jsonify({"error": f"Generation error: {str(e)}"}), 500
