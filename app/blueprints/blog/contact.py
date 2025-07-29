from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
)
from app.models.contact import ContactMessage
from app.core.extensions import db, mail
from app.models.setting import Setting
import requests

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    # Fetch site key (for form) from settings table with error handling
    try:
        recaptcha_site_row = Setting.query.filter_by(key="recaptcha_site_key").first()
        recaptcha_site_key = recaptcha_site_row.value if recaptcha_site_row else None
    except Exception as e:
        print(f"⚠️  Database query failed for recaptcha settings: {e}")
        recaptcha_site_key = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        ip = request.remote_addr
        honeypot = request.form.get("website", "")  # Hidden anti-bot field

        # Basic honeypot spam check
        if honeypot:
            flash("Spam detected. Try again.", "danger")
            return redirect(url_for("contact.contact"))

        # reCAPTCHA server-side validation
        recaptcha_response = request.form.get("g-recaptcha-response")
        try:
            recaptcha_secret_row = Setting.query.filter_by(
                key="recaptcha_secret_key"
            ).first()
            recaptcha_secret_key = (
                recaptcha_secret_row.value if recaptcha_secret_row else None
            )
        except Exception as e:
            print(f"⚠️  Database query failed for recaptcha secret: {e}")
            recaptcha_secret_key = None

        if recaptcha_site_key and recaptcha_secret_key:
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            resp = requests.post(
                verify_url,
                data={
                    "secret": recaptcha_secret_key,
                    "response": recaptcha_response,
                    "remoteip": ip,
                },
            )
            result = resp.json()
            if not result.get("success"):
                flash("reCAPTCHA verification failed. Please try again.", "danger")
                return redirect(url_for("contact.contact"))

        # Store in database with error handling
        try:
            contact = ContactMessage(name=name, email=email, message=message, ip=ip)
            db.session.add(contact)
            db.session.commit()
            flash("Message sent successfully! We'll reply soon.", "success")
        except Exception as e:
            print(f"⚠️  Failed to save contact message to database: {e}")
            flash("Thank you for your message! We'll get back to you soon.", "success")

        # Email notification (requires mail config to be set)
        try:
            from flask_mail import Message

            msg = Message(
                subject=f"New Contact Form Submission - {name}",
                sender=current_app.config.get(
                    "MAIL_DEFAULT_SENDER", "noreply@example.com"
                ),
                recipients=[
                    current_app.config.get("MAIL_DEFAULT_SENDER", "admin@example.com")
                ],
                body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}\nIP: {ip}",
            )
            mail.send(msg)
        except Exception as e:
            print(f"⚠️  Failed to send email notification: {e}")
            # Don't show error to user since message was already confirmed

        return redirect(url_for("contact.contact"))

    # Pass the reCAPTCHA site key to the template (for the widget)
    return render_template("contact.html", recaptcha_site_key=recaptcha_site_key)
