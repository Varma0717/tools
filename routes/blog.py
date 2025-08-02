from flask import Blueprint, render_template, abort
from utils.extensions import db
from models.post import Post


blog_bp = Blueprint("blog", __name__, url_prefix="/blog")


@blog_bp.route("/")
def blog_index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    # Pass posts with needed fields: title, slug, summary, image, author, author_img, category, date
    # Map or transform posts as needed
    return render_template("blog/index.html", posts=posts)


@blog_bp.route("/<slug>")
def view_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    return render_template("blog/post.html", post=post)
