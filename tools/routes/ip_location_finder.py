from flask import Blueprint, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, IPAddress
from flask_wtf.csrf import CSRFProtect
import requests

csrf = CSRFProtect()

ip_location_finder_bp = Blueprint('ip_location_finder', __name__, url_prefix='/tools')

class IPForm(FlaskForm):
    ip = StringField('IP Address', validators=[DataRequired(), IPAddress(message="Enter a valid IP address.")])
    submit = SubmitField('Find Location')

def get_ip_location(ip):
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=8)
        data = r.json()
        if 'error' in data:
            return {"error": data.get("reason", "IP lookup failed")}
        return {
            "ip": data.get("ip"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
            "org": data.get("org"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone")
        }
    except Exception as e:
        return {"error": str(e)}

@ip_location_finder_bp.route('/ip-location-finder', methods=['GET', 'POST'])
def ip_location_finder():
    form = IPForm()
    result = None
    if form.validate_on_submit():
        ip = form.ip.data.strip()
        result = get_ip_location(ip)
        if result.get("error"):
            flash(f"Error: {result['error']}", "danger")
    return render_template('tools/ip_location_finder.html', form=form, result=result)
