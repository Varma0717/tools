from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from models.contact import ContactMessage
from utils.extensions import db, mail
from admin.models.setting import Setting
import requests

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    # Fetch site key (for form) from settings table
    recaptcha_site_row = Setting.query.filter_by(key='recaptcha_site_key').first()
    recaptcha_site_key = recaptcha_site_row.value if recaptcha_site_row else None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        ip = request.remote_addr
        honeypot = request.form.get('website', '')  # Hidden anti-bot field

        # Basic honeypot spam check
        if honeypot:
            flash("Spam detected. Try again.", "danger")
            return redirect(url_for('contact.contact'))

        # reCAPTCHA server-side validation
        recaptcha_response = request.form.get('g-recaptcha-response')
        recaptcha_secret_row = Setting.query.filter_by(key='recaptcha_secret_key').first()
        recaptcha_secret_key = recaptcha_secret_row.value if recaptcha_secret_row else None

        if recaptcha_site_key and recaptcha_secret_key:
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            resp = requests.post(verify_url, data={
                'secret': recaptcha_secret_key,
                'response': recaptcha_response,
                'remoteip': ip
            })
            result = resp.json()
            if not result.get("success"):
                flash("reCAPTCHA verification failed. Please try again.", "danger")
                return redirect(url_for('contact.contact'))

        # Store in database
        contact = ContactMessage(name=name, email=email, message=message, ip=ip)
        db.session.add(contact)
        db.session.commit()

        # Email notification (requires mail config to be set)
        from flask_mail import Message
        msg = Message(
            subject=f"New Contact Form Submission - {name}",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[current_app.config['MAIL_DEFAULT_SENDER']],
            body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}\nIP: {ip}"
        )
        try:
            mail.send(msg)
            flash("Message sent successfully! We'll reply soon.", "success")
        except Exception as e:
            flash("Message saved but failed to send email. Please try later.", "warning")

        return redirect(url_for('contact.contact'))

    # Pass the reCAPTCHA site key to the template (for the widget)
    return render_template('contact.html', recaptcha_site_key=recaptcha_site_key)