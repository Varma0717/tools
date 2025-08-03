"""
Content Management Routes
========================
Post and content CRUD operations
"""

import os
import logging
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

# Core extensions
from utils.extensions import db

# Models
from models.post import Post
from models.newsletter import Subscriber

# Create blueprint
content_bp = Blueprint("admin_content", __name__, url_prefix="/admin")

logger = logging.getLogger(__name__)


def admin_required(func):
    """Admin-only access decorator"""

    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("users.dashboard"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return login_required(wrapper)


def save_file(file_storage):
    """Save uploaded file safely"""
    if file_storage and file_storage.filename != "":
        filename = secure_filename(file_storage.filename)
        path = os.path.join(current_app.root_path, "static", "images", filename)
        file_storage.save(path)
        return filename
    return None


@content_bp.route("/content")
@admin_required
def content_management():
    """Content management overview"""
    content_stats = get_content_stats()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    return render_template(
        "admin/content.html", stats=content_stats, recent_posts=recent_posts
    )


@content_bp.route("/posts")
@admin_required
def posts_list():
    """List all posts with pagination"""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")

    query = Post.query
    if search:
        query = query.filter(
            Post.title.contains(search) | Post.content.contains(search)
        )

    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin/posts_list.html", posts=posts, search=search)


@content_bp.route("/posts/create", methods=["GET", "POST"])
@admin_required
def posts_create():
    """Create new post"""
    if request.method == "POST":
        try:
            slug = request.form.get("slug", "").strip()
            if Post.query.filter_by(slug=slug).first():
                flash("Slug already exists. Please choose a different slug.", "error")
                return redirect(url_for("admin_content.posts_create"))

            image_filename = save_file(request.files.get("image"))
            author_img_filename = save_file(request.files.get("author_img"))
            featured_img_filename = save_file(request.files.get("featured_image"))

            post = Post(
                title=request.form.get("title", "").strip(),
                slug=slug,
                content=request.form.get("content", "").strip(),
                summary=request.form.get("summary", "").strip() or None,
                image=image_filename,
                featured_image=featured_img_filename,
                category=request.form.get("category", "").strip() or None,
                author=request.form.get("author", "").strip() or None,
                author_img=author_img_filename,
                meta_title=request.form.get("meta_title", "").strip() or None,
                meta_description=request.form.get("meta_description", "").strip()
                or None,
                meta_keywords=request.form.get("meta_keywords", "").strip() or None,
            )
            db.session.add(post)
            db.session.commit()
            flash("Post created successfully!", "success")
            return redirect(url_for("admin_content.posts_list"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating post: {str(e)}", "error")

    return render_template("admin/posts_create.html")


@content_bp.route("/posts/edit/<int:post_id>", methods=["GET", "POST"])
@admin_required
def posts_edit(post_id):
    """Edit existing post"""
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        try:
            slug = request.form.get("slug", "").strip()
            existing = Post.query.filter(Post.slug == slug, Post.id != post_id).first()
            if existing:
                flash("Slug already exists. Please choose a different slug.", "error")
                return redirect(url_for("admin_content.posts_edit", post_id=post_id))

            post.title = request.form.get("title", "").strip()
            post.slug = slug
            post.content = request.form.get("content", "").strip()
            post.summary = request.form.get("summary", "").strip() or None
            post.category = request.form.get("category", "").strip() or None
            post.author = request.form.get("author", "").strip() or None

            # Handle file uploads
            image_filename = save_file(request.files.get("image"))
            if image_filename:
                post.image = image_filename

            author_img_filename = save_file(request.files.get("author_img"))
            if author_img_filename:
                post.author_img = author_img_filename

            featured_img_filename = save_file(request.files.get("featured_image"))
            if featured_img_filename:
                post.featured_image = featured_img_filename

            post.meta_title = request.form.get("meta_title", "").strip() or None
            post.meta_description = (
                request.form.get("meta_description", "").strip() or None
            )
            post.meta_keywords = request.form.get("meta_keywords", "").strip() or None

            db.session.commit()
            flash("Post updated successfully!", "success")
            return redirect(url_for("admin_content.posts_list"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating post: {str(e)}", "error")

    return render_template("admin/posts_edit.html", post=post)


@content_bp.route("/posts/delete/<int:post_id>", methods=["POST"])
@admin_required
def posts_delete(post_id):
    """Delete post"""
    try:
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting post: {str(e)}", "error")

    return redirect(url_for("admin_content.posts_list"))


@content_bp.route("/subscribers")
@admin_required
def subscribers_management():
    """Manage newsletter subscribers"""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")

    query = Subscriber.query
    if search:
        query = query.filter(Subscriber.email.contains(search))

    subscribers = query.order_by(Subscriber.subscribed_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/subscribers_management.html", subscribers=subscribers, search=search
    )


@content_bp.route("/subscribers/export")
@admin_required
def subscribers_export():
    """Export subscribers list as CSV"""
    import csv
    import io
    from flask import make_response

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Email", "Subscribed Date"])

    subscribers = Subscriber.query.all()
    for subscriber in subscribers:
        writer.writerow(
            [subscriber.email, subscriber.subscribed_at.strftime("%Y-%m-%d %H:%M:%S")]
        )

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=subscribers.csv"

    return response


def get_content_stats():
    """Get content statistics"""
    try:
        total_posts = Post.query.count()
        published_posts = (
            Post.query.filter_by(published=True).count()
            if hasattr(Post, "published")
            else total_posts
        )

        return {
            "total_posts": total_posts,
            "published_posts": published_posts,
            "draft_posts": total_posts - published_posts,
        }
    except Exception as e:
        logger.error(f"Error getting content stats: {e}")
        return {"total_posts": 0, "published_posts": 0, "draft_posts": 0}
