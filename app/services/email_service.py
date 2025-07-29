"""
Email service for sending emails via SMTP.
"""

from flask import current_app, render_template_string
from flask_mail import Message
from app.core.extensions import mail
import logging


class EmailService:
    """Service for sending emails."""

    @staticmethod
    def send_email(to, subject, body, html_body=None, sender=None):
        """Send an email."""
        try:
            if not sender:
                sender = current_app.config.get("MAIL_DEFAULT_SENDER")

            msg = Message(
                subject=subject,
                recipients=[to] if isinstance(to, str) else to,
                body=body,
                html=html_body,
                sender=sender,
            )

            mail.send(msg)
            current_app.logger.info(f"Email sent successfully to {to}")
            return True

        except Exception as e:
            current_app.logger.error(f"Failed to send email to {to}: {str(e)}")
            return False

    @staticmethod
    def send_contact_notification(contact_data):
        """Send contact form notification to admin."""
        admin_email = (
            current_app.config.get("MAIL_USERNAME") or "admin@superseotoolkit.com"
        )

        subject = f"New Contact Form Submission: {contact_data['subject']}"

        body = f"""
New contact form submission received:

Name: {contact_data['name']}
Email: {contact_data['email']}
Subject: {contact_data['subject']}

Message:
{contact_data['message']}

---
Sent from Super SEO Toolkit Contact Form
        """

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                <h2 style="margin: 0;">New Contact Form Submission</h2>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #495057; margin-top: 0;">Contact Details</h3>
                    <p><strong>Name:</strong> {contact_data['name']}</p>
                    <p><strong>Email:</strong> <a href="mailto:{contact_data['email']}">{contact_data['email']}</a></p>
                    <p><strong>Subject:</strong> {contact_data['subject']}</p>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px;">
                    <h3 style="color: #495057; margin-top: 0;">Message</h3>
                    <p style="line-height: 1.6; white-space: pre-wrap;">{contact_data['message']}</p>
                </div>
                <div style="text-align: center; margin-top: 20px; color: #6c757d; font-size: 14px;">
                    <p>Sent from Super SEO Toolkit Contact Form</p>
                </div>
            </div>
        </div>
        """

        return EmailService.send_email(admin_email, subject, body, html_body)

    @staticmethod
    def send_contact_confirmation(user_email, user_name):
        """Send confirmation email to user who submitted contact form."""
        subject = "Thank you for contacting Super SEO Toolkit"

        body = f"""
Dear {user_name},

Thank you for contacting Super SEO Toolkit. We have received your message and will get back to you within 24 hours.

Our team is committed to providing excellent support and we appreciate your patience.

Best regards,
Super SEO Toolkit Support Team

---
This is an automated message. Please do not reply to this email.
        """

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                <h2 style="margin: 0;">Thank You for Contacting Us</h2>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                <div style="background: white; padding: 20px; border-radius: 8px;">
                    <p>Dear <strong>{user_name}</strong>,</p>
                    <p>Thank you for contacting <strong>Super SEO Toolkit</strong>. We have received your message and will get back to you within <strong>24 hours</strong>.</p>
                    <p>Our team is committed to providing excellent support and we appreciate your patience.</p>
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <p style="margin: 0; color: #1565c0;"><strong>💡 While you wait:</strong></p>
                        <p style="margin: 5px 0 0 0; color: #1565c0;">Check out our comprehensive documentation and SEO guides for immediate help.</p>
                    </div>
                    <p>Best regards,<br><strong>Super SEO Toolkit Support Team</strong></p>
                </div>
                <div style="text-align: center; margin-top: 20px; color: #6c757d; font-size: 14px;">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </div>
        """

        return EmailService.send_email(user_email, subject, body, html_body)

    @staticmethod
    def send_newsletter_welcome(user_email):
        """Send welcome email to new newsletter subscriber."""
        subject = "Welcome to Super SEO Toolkit Newsletter!"

        body = f"""
Welcome to Super SEO Toolkit Newsletter!

Thank you for subscribing to our newsletter. You'll receive:

• Latest SEO tips and strategies
• New tool announcements
• Industry insights and trends
• Exclusive content for subscribers

Stay tuned for valuable content to help you succeed with SEO!

Best regards,
Super SEO Toolkit Team

---
To unsubscribe, visit: [unsubscribe link]
        """

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Welcome to Our Newsletter!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Thank you for joining the Super SEO Toolkit community</p>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                <div style="background: white; padding: 25px; border-radius: 8px;">
                    <p style="font-size: 16px; line-height: 1.6;">Thank you for subscribing to our newsletter! You'll receive:</p>
                    <ul style="line-height: 1.8; color: #495057;">
                        <li>📈 <strong>Latest SEO tips and strategies</strong></li>
                        <li>🛠️ <strong>New tool announcements</strong></li>
                        <li>📊 <strong>Industry insights and trends</strong></li>
                        <li>🔐 <strong>Exclusive content for subscribers</strong></li>
                    </ul>
                    <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                        <p style="margin: 0; color: #2e7d32;"><strong>🎉 Welcome Gift</strong></p>
                        <p style="margin: 5px 0 0 0; color: #2e7d32;">Get 20% off your first premium subscription!</p>
                    </div>
                    <p>Stay tuned for valuable content to help you succeed with SEO!</p>
                    <p>Best regards,<br><strong>Super SEO Toolkit Team</strong></p>
                </div>
                <div style="text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px;">
                    <p>You're receiving this because you subscribed to our newsletter.</p>
                    <p><a href="#" style="color: #6c757d;">Unsubscribe</a> | <a href="#" style="color: #6c757d;">Update preferences</a></p>
                </div>
            </div>
        </div>
        """

        return EmailService.send_email(user_email, subject, body, html_body)
