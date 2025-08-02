import os
import logging
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.post import Post
from utils.extensions import db
from admin.forms import AdminSettingForm  # Assuming you have this form defined
from users.models.order import Order       # Assuming your Order model
from users.models.download import Download # Assuming your Download model
from admin.models import Setting           # Assuming your Setting model

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

logger = logging.getLogger(__name__)

def admin_only(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Unauthorized access", "danger")
            return redirect(url_for('users.dashboard'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return login_required(wrapper)

def save_file(file_storage):
    if file_storage and file_storage.filename != '':
        filename = secure_filename(file_storage.filename)
        path = os.path.join(current_app.root_path, "static", "images", filename)
        file_storage.save(path)
        return filename
    return None

@admin_bp.route('/', endpoint="panel")
@admin_only
def admin_panel():
    if current_user.role != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for('users.account'))
    return render_template("admin/dashboard.html")

# --- Section rendering helpers ---

def _render_overview():
    try:
        order_count = Order.query.count()
        download_count = Download.query.count()
        return render_template("admin/sections/overview.html",
                               order_count=order_count,
                               download_count=download_count,
                               user=current_user)
    except Exception as e:
        logger.error(f"Failed to render overview: {e}", exc_info=True)
        return render_template("admin/sections/error.html",
                               error="Failed to load overview"), 500

def _render_orders():
    try:
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return render_template("admin/sections/orders.html", orders=orders, user=current_user)
    except Exception as e:
        logger.error(f"Failed to render orders: {e}", exc_info=True)
        return render_template("admin/sections/error.html",
                               error="Failed to load orders"), 500

def _render_downloads():
    try:
        downloads = Download.query.order_by(Download.created_at.desc()).all()
        return render_template("admin/sections/downloads.html", downloads=downloads, user=current_user)
    except Exception as e:
        logger.error(f"Failed to render downloads: {e}", exc_info=True)
        return render_template("admin/sections/error.html",
                               error="Failed to load downloads"), 500

def _render_settings():
    try:
        form = AdminSettingForm()
        settings = Setting.query.all()
        return render_template("admin/sections/settings.html", form=form, settings=settings, user=current_user)
    except Exception as e:
        logger.error(f"Failed to render settings: {e}", exc_info=True)
        return render_template("admin/sections/error.html",
                               error="Failed to load settings"), 500

SECTION_DISPATCH = {
    "overview": _render_overview,
    "orders": _render_orders,
    "downloads": _render_downloads,
    "settings": _render_settings,
}

@admin_bp.route("/section/<name>")
@admin_only
def section(name):
    if name not in SECTION_DISPATCH:
        logger.warning(f"Admin requested unknown section: {name}")
        return render_template("admin/sections/404.html", section=name), 404

    try:
        return SECTION_DISPATCH[name]()
    except Exception as e:
        logger.error(f"Error rendering admin section '{name}': {e}", exc_info=True)
        return render_template("admin/sections/error.html", section=name, error=str(e)), 500

# --- Posts CRUD ---

@admin_bp.route('/posts')
@admin_only
def posts_list():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("admin/posts_list.html", posts=posts)

@admin_bp.route('/posts/create', methods=['GET', 'POST'])
@admin_only
def posts_create():
    if request.method == "POST":
        slug = request.form.get("slug", "").strip()
        if Post.query.filter_by(slug=slug).first():
            flash("Slug already exists. Please choose a different slug.", "error")
            return redirect(url_for('admin.posts_create'))

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
            meta_description=request.form.get("meta_description", "").strip() or None,
            meta_keywords=request.form.get("meta_keywords", "").strip() or None,
        )
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for('admin.posts_list'))

    return render_template("admin/posts_create.html")

@admin_bp.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_only
def posts_edit(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        slug = request.form.get("slug", "").strip()
        existing = Post.query.filter(Post.slug == slug, Post.id != post_id).first()
        if existing:
            flash("Slug already exists. Please choose a different slug.", "error")
            return redirect(url_for('admin.posts_edit', post_id=post_id))

        post.title = request.form.get("title", "").strip()
        post.slug = slug
        post.content = request.form.get("content", "").strip()
        post.summary = request.form.get("summary", "").strip() or None
        post.category = request.form.get("category", "").strip() or None
        post.author = request.form.get("author", "").strip() or None

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
        post.meta_description = request.form.get("meta_description", "").strip() or None
        post.meta_keywords = request.form.get("meta_keywords", "").strip() or None

        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for('admin.posts_list'))

    return render_template("admin/posts_edit.html", post=post)

@admin_bp.route('/posts/delete/<int:post_id>', methods=['POST'])
@admin_only
def posts_delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully.", "success")
    return redirect(url_for('admin.posts_list'))
