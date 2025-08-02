from datetime import datetime
from utils.extensions import db

class PageView(db.Model):
    __tablename__ = 'page_views'

    id = db.Column(db.Integer, primary_key=True)
    page_slug = db.Column(db.String(255), unique=True, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    last_viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def increment(self):
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()
