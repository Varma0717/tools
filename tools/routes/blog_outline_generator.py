from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError
from tools.utils.blog_outline_generator_utils import generate_blog_outline

blog_outline_generator_bp = Blueprint('blog_outline_generator', __name__, url_prefix='/tools/blog-outline-generator')

@blog_outline_generator_bp.route('/', methods=['GET'])
def blog_outline_generator():
    return render_template('tools/blog_outline_generator.html')

@blog_outline_generator_bp.route('/ajax', methods=['POST'])
def blog_outline_generator_ajax():
    try:
        csrf_token = request.headers.get('X-CSRFToken') or request.json.get('csrf_token')
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    data = request.get_json() or {}
    topic = data.get('topic', '').strip()
    desc = data.get('desc', '').strip()

    if not topic or len(topic) < 3:
        return jsonify({"error": "Please enter a valid blog topic."}), 400

    outline, error = generate_blog_outline(topic, desc)
    if outline:
        return jsonify({"outline": outline})
    else:
        return jsonify({"error": f"Error generating outline: {error}"}), 500
