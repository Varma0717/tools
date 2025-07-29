from flask import Blueprint, render_template, abort
from app.core.extensions import db
from app.models.post import Post


blog_bp = Blueprint("blog", __name__, url_prefix="/blog")


@blog_bp.route("/")
def blog_index():
    """Display all blog posts from database"""
    try:
        # Get all posts ordered by creation date (newest first)
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("blog/index.html", posts=posts)
    except Exception as e:
        print(f"⚠️  Blog query failed, using static data: {e}")
        # Fallback to static data if database query fails
        posts = [
            {
                "title": "SEO Best Practices for 2025",
                "slug": "seo-best-practices-2025",
                "summary": "Discover the latest SEO techniques and strategies for the new year.",
                "image": None,
                "author": "SEO Expert",
                "author_img": None,
                "category": "SEO",
                "created_at": "2025-01-01",
            },
            {
                "title": "Meta Tags Optimization Guide",
                "slug": "meta-tags-optimization-guide",
                "summary": "Learn how to optimize your meta tags for better search engine visibility.",
                "image": None,
                "author": "SEO Expert",
                "author_img": None,
                "category": "SEO",
                "created_at": "2025-01-02",
            },
        ]
        return render_template("blog/index.html", posts=posts)


@blog_bp.route("/<slug>")
def view_post(slug):
    """Display individual blog post by slug"""
    try:
        # Get post from database
        post = Post.query.filter_by(slug=slug).first()
        if not post:
            abort(404)
        return render_template("blog/post.html", post=post)
    except Exception as e:
        print(f"⚠️  Post query failed: {e}")
        # Fallback for specific posts
        if slug == "seo-best-practices-2025":
            post = {
                "title": "SEO Best Practices for 2025",
                "slug": "seo-best-practices-2025",
                "content": "This is a sample blog post about SEO best practices...",
                "summary": "Discover the latest SEO techniques and strategies for the new year.",
                "image": None,
                "author": "SEO Expert",
                "author_img": None,
                "category": "SEO",
                "created_at": "2025-01-01",
            }
            return render_template("blog/post.html", post=post)
        else:
            abort(404)
