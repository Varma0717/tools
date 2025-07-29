from app.core.extensions import db
from datetime import datetime


class ContactMessage(db.Model):
    __tablename__ = "contact_message"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    ip = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContactMessage {self.name}>"


# Alias for backward compatibility
Contact = ContactMessage
