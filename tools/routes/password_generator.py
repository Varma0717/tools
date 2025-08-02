from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
import random
import string

csrf = CSRFProtect()
password_generator_bp = Blueprint('password_generator', __name__, url_prefix='/tools')

def generate_password(length, uppercase, lowercase, digits, symbols):
    chars = ''
    if uppercase:
        chars += string.ascii_uppercase
    if lowercase:
        chars += string.ascii_lowercase
    if digits:
        chars += string.digits
    if symbols:
        chars += string.punctuation
    if not chars:
        chars = string.ascii_letters
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

@password_generator_bp.route('/password-generator', methods=['GET'])
def password_generator():
    csrf_token = generate_csrf()
    return render_template('tools/password_generator.html', csrf_token=csrf_token)

@password_generator_bp.route('/password-generator/ajax', methods=['POST'])
@csrf.exempt
def password_generator_ajax():
    data = request.get_json()
    print("DEBUG: Received data:", data)   # <-- Add this for debugging!
    try:
        length = int(data.get('length', 16))
        uppercase = data.get('uppercase', True)
        lowercase = data.get('lowercase', True)
        digits = data.get('digits', True)
        symbols = data.get('symbols', True)
        if not any([uppercase, lowercase, digits, symbols]):
            lowercase = True
        password = generate_password(length, uppercase, lowercase, digits, symbols)
        return jsonify({'password': password})
    except Exception as e:
        print("Password AJAX error:", e)
        return jsonify({'error': 'Failed to generate password: ' + str(e)}), 400