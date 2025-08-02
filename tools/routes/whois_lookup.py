from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
import whois
import re

csrf = CSRFProtect()

whois_lookup_bp = Blueprint('whois_lookup', __name__, url_prefix='/tools')

class WhoisForm(FlaskForm):
    url = StringField('Domain URL', validators=[DataRequired()], render_kw={"placeholder": "example.com"})
    submit = SubmitField('Lookup Whois')

def parse_domain(url):
    url = url.strip().lower()
    url = re.sub(r'^https?://', '', url)
    url = url.split('/')[0]
    url = url.replace('www.', '')
    return url

def perform_whois_lookup(domain):
    try:
        w = whois.whois(domain)
        if not w or not w.domain_name:
            return None, "No WHOIS data found for this domain."
        whois_dict = {str(k): str(v) for k, v in dict(w).items() if v}
        return whois_dict, None
    except Exception as e:
        return None, f"Error: {str(e)}"

@whois_lookup_bp.route('/whois-lookup', methods=['GET'])
def whois_lookup():
    csrf_token = generate_csrf()
    form = WhoisForm()
    return render_template('tools/whois_lookup.html', form=form, csrf_token=csrf_token)

@whois_lookup_bp.route('/whois-lookup/ajax', methods=['POST'])
@csrf.exempt
def whois_lookup_ajax():
    data = request.get_json()
    url = data.get('url', '').strip()
    if not url or len(url) < 4:
        return jsonify({"error": "Please enter a valid domain name."}), 400

    domain = parse_domain(url)
    whois_data, error = perform_whois_lookup(domain)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"whois": whois_data})
