from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.title_tag_generator_utils import generate_title_tag

title_tag_generator_bp = Blueprint('title_tag_generator', __name__, url_prefix='/tools/title-tag-generator')

@title_tag_generator_bp.route('/', methods=['GET'])
def title_tag_generator():
    return render_template('tools/title_tag_generator.html', csrf_token=generate_csrf())

@title_tag_generator_bp.route('/ajax', methods=['POST'])
def title_tag_generator_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        topic = request.form.get("topic", "").strip()
        if not topic:
            return jsonify({'error': 'Please enter a topic or keyword.'}), 400

        result, error = generate_title_tag(topic)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
