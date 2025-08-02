from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.grammar_checker_utils import check_grammar

grammar_checker_bp = Blueprint('grammar_checker', __name__, url_prefix='/tools/grammar-checker')

@grammar_checker_bp.route('/', methods=['GET'])
def grammar_checker():
    return render_template('tools/grammar_checker.html', csrf_token=generate_csrf())

@grammar_checker_bp.route('/ajax', methods=['POST'])
def grammar_checker_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))

        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({'error': 'Please enter some text to check.'}), 400

        result, error = check_grammar(text)
        if error:
            return jsonify({'error': error}), 500

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
