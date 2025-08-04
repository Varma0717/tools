from utils.extensions import db
from datetime import datetime
from sqlalchemy import Text, Index


# Association table for many-to-many relationship between posts and categories
post_categories = db.Table(
    "post_categories",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column(
        "category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True
    ),
    db.Column("created_at", db.DateTime, default=datetime.utcnow),
)

# Association table for many-to-many relationship between posts and tags
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow),
)


class Post(db.Model):
    __tablename__ = "posts"

    # Primary Fields
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    content = db.Column(Text, nullable=False)
    excerpt = db.Column(Text, nullable=True)  # Short summary for previews

    # Media - featured_image serves as both main image and OG image
    featured_image = db.Column(db.String(500), nullable=True)

    # Author Information
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    author_name = db.Column(db.String(150), nullable=True)  # Fallback if no user

    # SEO Fields
    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)
    meta_keywords = db.Column(db.String(500), nullable=True)

    # Publishing Control
    status = db.Column(
        db.String(20), default="draft", index=True
    )  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False, index=True)
    priority = db.Column(db.Integer, default=0)  # For sorting/featuring

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    published_at = db.Column(db.DateTime, nullable=True, index=True)

    # Analytics
    view_count = db.Column(db.Integer, default=0)
    read_time_minutes = db.Column(db.Integer, default=5)  # Estimated read time

    # Relationships
    author = db.relationship("User", backref="posts", foreign_keys=[author_id])
    categories = db.relationship("Category", secondary=post_categories, backref="posts")
    tags = db.relationship("Tag", secondary=post_tags, backref="posts")

    # Indexes
    __table_args__ = (
        Index("idx_post_status_published", "status", "published_at"),
        Index("idx_post_featured_status", "is_featured", "status"),
        Index("idx_post_priority_published", "priority", "published_at"),
    )

    def __init__(self, title, slug, content, **kwargs):
        self.title = title
        self.slug = slug
        self.content = content

        # Set optional fields
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)

        # Auto-generate excerpt if not provided
        if not self.excerpt and content:
            self.excerpt = self._generate_excerpt(content)

        # Estimate read time
        if content:
            self.read_time_minutes = self._estimate_read_time(content)

    def _generate_excerpt(self, content, max_length=200):
        """Generate excerpt from content"""
        import re

        # Remove HTML tags and get plain text
        clean_text = re.sub(r"<[^>]+>", "", content)
        if len(clean_text) <= max_length:
            return clean_text
        return clean_text[:max_length].rsplit(" ", 1)[0] + "..."

    def _estimate_read_time(self, content):
        """Estimate reading time in minutes (average 200 words per minute)"""
        import re

        word_count = len(re.findall(r"\w+", content))
        return max(1, round(word_count / 200))

    @property
    def is_published(self):
        """Check if post is published"""
        return self.status == "published" and self.published_at is not None

    @property
    def display_author(self):
        """Get display name for author"""
        if self.author:
            return self.author.username
        return self.author_name or "Anonymous"

    @property
    def og_image(self):
        """Get Open Graph image (same as featured image)"""
        return self.featured_image

    @property
    def category_names(self):
        """Get list of category names"""
        return [cat.name for cat in self.categories]

    @property
    def tag_names(self):
        """Get list of tag names"""
        return [tag.name for tag in self.tags]

    def publish(self):
        """Publish the post"""
        self.status = "published"
        if not self.published_at:
            self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def unpublish(self):
        """Unpublish the post"""
        self.status = "draft"
        self.updated_at = datetime.utcnow()

    def increment_views(self):
        """Increment view count"""
        self.view_count += 1

    def to_dict(self):
        """Convert post to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "content": self.content,
            "excerpt": self.excerpt,
            "featured_image": self.featured_image,
            "author_name": self.display_author,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "status": self.status,
            "is_featured": self.is_featured,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": (
                self.published_at.isoformat() if self.published_at else None
            ),
            "view_count": self.view_count,
            "read_time_minutes": self.read_time_minutes,
            "categories": self.category_names,
            "tags": self.tag_names,
            "og_image": self.og_image,
        }

    @classmethod
    def get_published(cls):
        """Get all published posts ordered by published date"""
        return cls.query.filter_by(status="published").order_by(cls.published_at.desc())

    @classmethod
    def get_featured(cls, limit=5):
        """Get featured published posts"""
        return (
            cls.query.filter_by(status="published", is_featured=True)
            .order_by(cls.priority.desc(), cls.published_at.desc())
            .limit(limit)
        )

    @classmethod
    def get_by_category(cls, category_slug):
        """Get published posts by category"""
        from .category import Category

        return (
            cls.query.join(cls.categories)
            .filter(Category.slug == category_slug, cls.status == "published")
            .order_by(cls.published_at.desc())
        )

    @classmethod
    def get_by_tag(cls, tag_slug):
        """Get published posts by tag"""
        from .tag import Tag

        return (
            cls.query.join(cls.tags)
            .filter(Tag.slug == tag_slug, cls.status == "published")
            .order_by(cls.published_at.desc())
        )

    def __repr__(self):
        return f"<Post {self.title} ({self.status})>"
