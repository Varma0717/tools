from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import CSRFProtect, generate_csrf
import dns.resolver

csrf = CSRFProtect()

dns_lookup_bp = Blueprint('dns_lookup', __name__, url_prefix='/tools')

class DNSLookupForm(FlaskForm):
    url = StringField('Domain URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Lookup DNS Records')

def perform_dns_lookup(domain):
    # Strip protocol and path
    domain = domain.split("//")[-1].split("/")[0]
    record_types = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA"]
    results = []
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type, lifetime=4)
            for rdata in answers:
                results.append({"type": record_type, "value": str(rdata)})
        except Exception:
            continue
    return results if results else [{"type": "No Records", "value": "No DNS records found or domain invalid."}]

@dns_lookup_bp.route('/dns-lookup', methods=['GET'])
def dns_lookup():
    csrf_token = generate_csrf()
    form = DNSLookupForm()
    return render_template('tools/dns_lookup.html', form=form, csrf_token=csrf_token)

@dns_lookup_bp.route('/dns-lookup/ajax', methods=['POST'])
@csrf.exempt
def dns_lookup_ajax():
    data = request.get_json()
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'success': False, 'error': 'No domain provided.'}), 400
    try:
        results = perform_dns_lookup(url)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
