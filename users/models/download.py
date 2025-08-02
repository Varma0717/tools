# users/models/download.py
from utils.extensions import db
from datetime import datetime

class Download(db.Model):
    __tablename__ = 'download'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_name = db.Column(db.String(100))
    download_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)