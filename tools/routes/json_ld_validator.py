from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from wtforms import TextAreaField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
import json

csrf = CSRFProtect()

json_ld_validator_bp = Blueprint('json_ld_validator', __name__, url_prefix='/tools')

class JSONLDForm(FlaskForm):
    jsonld = TextAreaField('Paste your JSON-LD code', validators=[DataRequired()])
    submit = SubmitField('Validate JSON-LD')

def validate_json_ld(json_str):
    try:
        data = json.loads(json_str)
        # Optionally check for @context or @type fields for JSON-LD (optional)
        if isinstance(data, dict) and "@context" in data:
            return True, "✅ Valid JSON-LD: Syntax and @context detected."
        elif isinstance(data, list) and data and "@context" in data[0]:
            return True, "✅ Valid JSON-LD: Syntax and @context detected (array)."
        else:
            return True, "✅ Valid JSON syntax, but @context not found (still likely valid)."
    except Exception as e:
        return False, f"❌ Invalid JSON-LD: {str(e)}"

@json_ld_validator_bp.route('/json-ld-validator', methods=['GET'])
def json_ld_validator():
    csrf_token = generate_csrf()
    return render_template('tools/json_ld_validator.html', csrf_token=csrf_token)

@json_ld_validator_bp.route('/json-ld-validator/ajax', methods=['POST'])
@csrf.exempt
def json_ld_validator_ajax():
    data = request.get_json()
    code = data.get('jsonld', '').strip()
    if not code:
        return jsonify({"valid": False, "message": "Please paste your JSON-LD code."}), 400
    is_valid, message = validate_json_ld(code)
    return jsonify({"valid": is_valid, "message": message})
