from utils.extensions import db
from datetime import datetime


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)  # post image (thumbnail)
    featured_image = db.Column(db.String(255), nullable=True)  # OG image / featured for SEO
    category = db.Column(db.String(100), nullable=True)
    author = db.Column(db.String(100), nullable=True)
    author_img = db.Column(db.String(255), nullable=True)

    # SEO fields
    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)
    meta_keywords = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(
        self,
        title,
        slug,
        content,
        summary=None,
        image=None,
        featured_image=None,
        category=None,
        author=None,
        author_img=None,
        meta_title=None,
        meta_description=None,
        meta_keywords=None,
    ):
        self.title = title
        self.slug = slug
        self.content = content
        self.summary = summary
        self.image = image
        self.featured_image = featured_image
        self.category = category
        self.author = author
        self.author_img = author_img
        self.meta_title = meta_title
        self.meta_description = meta_description
        self.meta_keywords = meta_keywords

    # ... existing methods (repr, to_dict, save, update, delete, etc.) unchanged

