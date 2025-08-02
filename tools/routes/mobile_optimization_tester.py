from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from tools.utils.mobile_optimization_tester_utils import test_mobile_optimization

mobile_tester_bp = Blueprint('mobile_tester', __name__, url_prefix='/tools/mobile-optimization')

@mobile_tester_bp.route('/', methods=['GET'])
def mobile_tester():
    return render_template('tools/mobile_optimization_tester.html', csrf_token=generate_csrf())

@mobile_tester_bp.route('/ajax', methods=['POST'])
def mobile_tester_ajax():
    try:
        validate_csrf(request.form.get("csrf_token"))
        url = request.form.get("url", "").strip()
        if not url:
            return jsonify({'error': 'Please enter a valid URL.'}), 400

        results = test_mobile_optimization(url)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
