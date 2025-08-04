from flask import Blueprint, render_template, abort, request, jsonify
from utils.extensions import db
from models.post import Post
from models.category import Category
from models.tag import Tag
from sqlalchemy import or_

blog_bp = Blueprint("blog", __name__, url_prefix="/blog")


@blog_bp.route("/")
def blog_index():
    """Blog index page with pagination and filtering"""
    page = request.args.get("page", 1, type=int)
    category_slug = request.args.get("category")
    tag_slug = request.args.get("tag")
    search = request.args.get("search", "").strip()

    # Base query for published posts
    query = Post.get_published()

    # Apply filters
    if category_slug:
        query = Post.get_by_category(category_slug)
    elif tag_slug:
        query = Post.get_by_tag(tag_slug)
    elif search:
        query = query.filter(
            or_(
                Post.title.contains(search),
                Post.content.contains(search),
                Post.excerpt.contains(search),
            )
        )

    # Pagination
    per_page = 12  # Posts per page
    posts = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get featured posts for sidebar
    featured_posts = Post.get_featured(limit=5).all()

    # Get categories for navigation
    categories = (
        Category.query.filter_by(is_active=True)
        .order_by(Category.sort_order, Category.name)
        .all()
    )

    # Get popular tags
    popular_tags = Tag.query.limit(20).all()

    return render_template(
        "blog/index.html",
        posts=posts,
        featured_posts=featured_posts,
        categories=categories,
        popular_tags=popular_tags,
        current_category=category_slug,
        current_tag=tag_slug,
        search_query=search,
    )


@blog_bp.route("/<slug>")
def view_post(slug):
    """View individual blog post"""
    post = Post.query.filter_by(slug=slug, status="published").first()
    if not post:
        abort(404)

    # Increment view count
    post.increment_views()
    db.session.commit()

    # Get related posts (same categories)
    related_posts = []
    if post.categories:
        related_posts = (
            Post.query.join(Post.categories)
            .filter(
                Category.id.in_([cat.id for cat in post.categories]),
                Post.id != post.id,
                Post.status == "published",
            )
            .limit(4)
            .all()
        )

    # Get recent posts if no related posts
    if not related_posts:
        related_posts = Post.get_published().filter(Post.id != post.id).limit(4).all()

    return render_template("blog/post.html", post=post, related_posts=related_posts)


@blog_bp.route("/category/<slug>")
def category_posts(slug):
    """View posts by category"""
    category = Category.query.filter_by(slug=slug, is_active=True).first()
    if not category:
        abort(404)

    page = request.args.get("page", 1, type=int)
    posts = Post.get_by_category(slug).paginate(page=page, per_page=12, error_out=False)

    return render_template("blog/category.html", category=category, posts=posts)


@blog_bp.route("/tag/<slug>")
def tag_posts(slug):
    """View posts by tag"""
    tag = Tag.query.filter_by(slug=slug).first()
    if not tag:
        abort(404)

    page = request.args.get("page", 1, type=int)
    posts = Post.get_by_tag(slug).paginate(page=page, per_page=12, error_out=False)

    return render_template("blog/tag.html", tag=tag, posts=posts)


@blog_bp.route("/api/search")
def search_posts():
    """API endpoint for blog search"""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"posts": []})

    posts = (
        Post.get_published()
        .filter(
            or_(
                Post.title.contains(query),
                Post.content.contains(query),
                Post.excerpt.contains(query),
            )
        )
        .limit(10)
        .all()
    )

    return jsonify(
        {
            "posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "excerpt": post.excerpt or post.title,
                    "url": f"/blog/{post.slug}",
                }
                for post in posts
            ]
        }
    )


@blog_bp.route("/track-view/<int:post_id>", methods=["POST"])
def track_view(post_id):
    """Track post view for analytics"""
    try:
        post = Post.query.get_or_404(post_id)
        post.view_count = (post.view_count or 0) + 1
        db.session.commit()
        return jsonify({"success": True, "views": post.view_count})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
