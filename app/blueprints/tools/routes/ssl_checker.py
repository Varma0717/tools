from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
import ssl
import socket
import datetime
from urllib.parse import urlparse

ssl_checker_bp = Blueprint("ssl_checker", __name__, url_prefix="/tools")


class SSLForm(FlaskForm):
    url = StringField("Website URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Check SSL Certificate")


def check_ssl_certificate(url):
    """Check SSL certificate of a given URL"""
    try:
        # Parse URL to get hostname
        parsed = urlparse(
            url if url.startswith(("http://", "https://")) else "https://" + url
        )
        hostname = parsed.hostname
        port = parsed.port or 443

        # Get SSL certificate
        context = ssl.create_default_context()

        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                # Parse certificate information
                results = {
                    "hostname": hostname,
                    "port": port,
                    "subject": dict(x[0] for x in cert["subject"]),
                    "issuer": dict(x[0] for x in cert["issuer"]),
                    "version": cert["version"],
                    "serial_number": cert["serialNumber"],
                    "not_before": cert["notBefore"],
                    "not_after": cert["notAfter"],
                }

                # Calculate days until expiration
                expiry_date = datetime.datetime.strptime(
                    cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                )
                days_remaining = (expiry_date - datetime.datetime.now()).days

                results["days_remaining"] = days_remaining
                results["expires_soon"] = days_remaining < 30
                results["expired"] = days_remaining < 0

                # Check for SAN (Subject Alternative Names)
                san_list = []
                if "subjectAltName" in cert:
                    san_list = [
                        name[1] for name in cert["subjectAltName"] if name[0] == "DNS"
                    ]
                results["san"] = san_list

                return results

    except ssl.SSLError as e:
        return {"error": f"SSL Error: {str(e)}"}
    except socket.error as e:
        return {"error": f"Connection Error: {str(e)}"}
    except Exception as e:
        return {"error": f"Analysis Error: {str(e)}"}


@ssl_checker_bp.route("/ssl-checker", methods=["GET"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def ssl_checker():
    csrf_token = generate_csrf()
    form = SSLForm()
    return render_template("tools/ssl_checker.html", form=form, csrf_token=csrf_token)


@ssl_checker_bp.route("/ssl-checker/ajax", methods=["POST"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def ssl_checker_ajax():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "No URL provided."}), 400

    try:
        results = check_ssl_certificate(url)
        if "error" in results:
            return jsonify({"success": False, "error": results["error"]}), 400

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
\n\nssl_checker_bp = Blueprint("ssl_checker", __name__, url_prefix="/tools")\n

@ssl_checker_bp.route("/ssl-checker/")
def ssl_checker_page():
    """Ssl Checker main page."""
    return render_template("tools/ssl_checker.html", csrf_token=generate_csrf())
