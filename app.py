from dotenv import load_dotenv

load_dotenv()

from routes.seo_analysis import seo_bp
from flask import request, Flask, render_template, jsonify

from flask_wtf.csrf import CSRFProtect

from flask_dance.contrib.google import make_google_blueprint, google
from utils.extensions import db, login_manager, mail, migrate
from users.routes import users_bp
from admin.routes import admin_bp
from admin.enhanced_routes import enhanced_admin_bp
from tools.routes import tools_bp, register_tool_blueprints
from tools.routes.sitemap import sitemap_bp
from models.newsletter import Subscriber
from auth.routes import auth_bp
from routes.blog import blog_bp
from models.post import Post

import os
import re

import logging

# Load environment variables


from logging.handlers import RotatingFileHandler


if not os.path.exists("logs"):
    os.mkdir("logs")

file_handler = RotatingFileHandler("logs/flask_app.log", maxBytes=10240, backupCount=10)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    )
)
file_handler.setLevel(logging.ERROR)

app = Flask(__name__)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.ERROR)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")


# --- Add your mail config here ---
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() in [
    "true",
    "1",
    "yes",
]
app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "false").lower() in [
    "true",
    "1",
    "yes",
]
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")  # <--- THIS LINE

# Init extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
mail.init_app(app)
csrf = CSRFProtect(app)

# Google OAuth Blueprint
google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    redirect_url=os.getenv("GOOGLE_REDIRECT_URI", "/login/google/authorized"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ],
)
app.register_blueprint(google_bp, url_prefix="/login")

# Register Blueprints
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(enhanced_admin_bp)
app.register_blueprint(tools_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(sitemap_bp)
app.register_blueprint(blog_bp)

# Register CRM and Analytics blueprints
from routes.analytics import analytics_bp
from routes.crm import crm_bp
from routes.subscription import subscription_bp

app.register_blueprint(analytics_bp, name="analytics_main")
app.register_blueprint(crm_bp)
app.register_blueprint(subscription_bp)


# User loader
from users.models import User

register_tool_blueprints(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from routes.contact import contact_bp
from routes.api import api_bp

app.register_blueprint(contact_bp)
app.register_blueprint(api_bp)
app.register_blueprint(seo_bp, url_prefix="/seo")


# ========================
# Newsletter Subscribe API
# ========================
@csrf.exempt
@app.route("/subscribe", methods=["POST"])
def subscribe():
    try:
        data = request.get_json()
        email = data.get("email", "").strip()

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"message": "Invalid email address."}), 400

        if Subscriber.query.filter_by(email=email).first():
            return jsonify({"message": "You're already subscribed."}), 200

        new_subscriber = Subscriber(email=email)
        db.session.add(new_subscriber)
        db.session.commit()

        return jsonify({"message": "Thank you for subscribing!"}), 200
    except Exception as e:
        print(f"[Subscribe Error] {e}")
        return jsonify({"message": "Something went wrong."}), 500


# ========================
# Homepage Route
# ========================
from models.category import Category


@app.route("/")
def home():
    # Fetch recent posts from database, order by created_at descending, limit 6
    recent_posts_db = Post.query.order_by(Post.created_at.desc()).limit(3).all()

    # Format posts for template: add image URL using url_for static path
    recent_posts = []
    for post in recent_posts_db:
        recent_posts.append(
            {
                "title": post.title,
                "slug": post.slug,
                "summary": post.summary or (post.content[:120] + "..."),
                "image": post.image,
            }
        )

    testimonials = [
        {
            "name": "Neha Sharma",
            "company": "Growth Labs",
            "message": "Super SEO Toolkit made my website audits a breeze! The AI suggestions are spot on and easy to implement.",
        },
        {
            "name": "David Lee",
            "company": "WebRise Agency",
            "message": "The dashboard is modern and intuitive. I especially love the real-time reports and downloadable PDFs for my clients.",
        },
        {
            "name": "Priya Verma",
            "company": "Freelance SEO",
            "message": "Keyword and backlink tools are super accurate. My site’s performance improved within weeks. Highly recommended!",
        },
    ]

    faqs = [
        {
            "question": "Is Super SEO Toolkit free to use?",
            "answer": "Yes! Most tools are free. Some advanced features require a premium plan for unlimited usage.",
        },
        {
            "question": "Do I need to register to use the tools?",
            "answer": "You can use most tools without an account. Registration gives you access to history, reports, and premium tools.",
        },
        {
            "question": "Are my website scans private?",
            "answer": "Absolutely. Your data and reports are confidential and visible only to you in your account dashboard.",
        },
        {
            "question": "Can I download PDF reports?",
            "answer": "Yes, you can generate and download detailed PDF reports for all audits and checks.",
        },
        {
            "question": "Do you support WordPress, Shopify, and custom sites?",
            "answer": "Yes! Our tools work for all popular platforms including WordPress, Shopify, Magento, HTML, and more.",
        },
    ]

    categories = [
        {"name": "Meta Tags Tools", "slug": "meta-tags-tools", "icon": "tag"},
        {
            "name": "AI Writing Generators",
            "slug": "ai-writing-generators",
            "icon": "pen-tool",
        },
        {
            "name": "Website Management Tools",
            "slug": "website-management-tools",
            "icon": "settings",
        },
        {"name": "Keyword Tools", "slug": "keyword-tools", "icon": "search"},
        {"name": "Backlink Tools", "slug": "backlink-tools", "icon": "link"},
        {"name": "PDF Tools", "slug": "pdf-tools", "icon": "file-text"},
        {"name": "Domain Tools", "slug": "domain-tools", "icon": "globe"},
        {"name": "Image Tools", "slug": "image-tools", "icon": "image"},
    ]

    return render_template(
        "home.html",
        recent_posts=recent_posts,
        testimonials=testimonials,
        faqs=faqs,
        categories=categories,
    )


# ========================
# Other Static Pages
# ========================
@app.route("/pricing", endpoint="pricing")
def pricing():
    return render_template("pricing.html")


@app.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")  # Make sure this template exists


@app.route("/terms-and-conditions")
def terms():
    return render_template("terms.html")


@app.route("/cookies-policy")
def cookies():
    return render_template("cookies.html")


@app.route("/about-us")
def about_us():
    return render_template("about.html")


@app.route("/ui-showcase")
def ui_showcase():
    return render_template("ui_showcase.html")


# for rule in app.url_map.iter_rules():
#    print(f"Route: {rule} --> endpoint: {rule.endpoint}")
