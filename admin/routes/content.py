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
    jsonify,
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
        if not current_user.is_authenticated:
            if request.is_json or request.path.startswith("/admin/api/"):
                return (
                    jsonify({"success": False, "message": "Authentication required"}),
                    401,
                )
            return redirect(url_for("users.dashboard"))

        if current_user.role != "admin":
            if request.is_json or request.path.startswith("/admin/api/"):
                return (
                    jsonify({"success": False, "message": "Admin access required"}),
                    403,
                )
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

    # Debug logging
    logger.info(f"Posts list accessed by user: {current_user.username}")
    logger.info(f"Posts count: {posts.total}")
    logger.info(f"Template: admin/posts_list.html")

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


@content_bp.route("/api/posts/bulk-actions", methods=["POST"])
@admin_required
def bulk_post_actions():
    """Handle bulk actions on posts"""
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"success": False, "message": "No JSON data provided"}), 400

        action = request_data.get("action")
        post_ids = request_data.get("post_ids", [])

        if not action or not post_ids:
            return (
                jsonify(
                    {"success": False, "message": "Action and post_ids are required"}
                ),
                400,
            )

        # Convert post_ids to integers
        try:
            post_ids = [int(pid) for pid in post_ids]
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "Invalid post IDs"}), 400

        # Get posts to modify
        posts = Post.query.filter(Post.id.in_(post_ids)).all()
        if not posts:
            return jsonify({"success": False, "message": "No posts found"}), 404

        processed_count = 0

        if action == "publish":
            for post in posts:
                if hasattr(post, "published"):
                    post.published = True
                    processed_count += 1
            message = f"Published {processed_count} posts successfully"

        elif action == "unpublish":
            for post in posts:
                if hasattr(post, "published"):
                    post.published = False
                    processed_count += 1
            message = f"Unpublished {processed_count} posts successfully"

        elif action == "delete":
            for post in posts:
                db.session.delete(post)
                processed_count += 1
            message = f"Deleted {processed_count} posts successfully"

        else:
            return jsonify({"success": False, "message": "Invalid action"}), 400

        # Commit changes
        db.session.commit()

        logger.info(
            f"Bulk action '{action}' performed on {processed_count} posts by user {current_user.id}"
        )
        return jsonify(
            {"success": True, "message": message, "processed_count": processed_count}
        )

    except Exception as e:
        db.session.rollback()
        error_msg = f"Error performing bulk action: {str(e)}"
        logger.error(error_msg)
        return jsonify({"success": False, "message": error_msg}), 500
