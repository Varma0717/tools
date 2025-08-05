# Suppress pkg_resources deprecation warnings from third-party libraries
import warnings

warnings.filterwarnings(
    "ignore", message="pkg_resources is deprecated as an API.*", category=UserWarning
)

from dotenv import load_dotenv

load_dotenv()

from routes.seo_analysis import seo_bp
from flask import (
    request,
    Flask,
    render_template,
    jsonify,
    redirect,
    url_for,
    current_app,
)

from flask_wtf.csrf import CSRFProtect

from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import current_user
from utils.extensions import db, login_manager, mail, migrate
from users.routes import users_bp
from admin import register_admin_routes
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

# TinyMCE Configuration
app.config["TINYMCE_API_KEY"] = os.getenv("TINYMCE_API_KEY", "no-api-key")

# Init extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
mail.init_app(app)
csrf = CSRFProtect(app)


# Make CSRF token available in templates
@app.context_processor
def inject_csrf_token():
    try:
        from flask_wtf.csrf import generate_csrf

        token = generate_csrf()
        return dict(csrf_token=lambda: token)
    except Exception:
        return dict(csrf_token=lambda: "")


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
register_admin_routes(app)  # Register all admin route blueprints
app.register_blueprint(tools_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(sitemap_bp)
app.register_blueprint(blog_bp)

# Register CRM and Analytics blueprints
from routes.analytics import analytics_bp
from routes.pricing import pricing_bp
from routes.crm import crm_bp
from routes.subscription import subscription_bp
from routes.business import business_bp

app.register_blueprint(analytics_bp, name="analytics_main")
app.register_blueprint(crm_bp)
app.register_blueprint(subscription_bp)
app.register_blueprint(pricing_bp)
app.register_blueprint(business_bp)


# Import models to ensure SQLAlchemy recognizes them
from users.models import User
from models.tool_usage import ToolUsage, Subscription, ToolAnalytics

register_tool_blueprints(app)


@login_manager.user_loader
def load_user(user_id):
    from utils.extensions import db

    return db.session.get(User, int(user_id))


from routes.contact import contact_bp
from routes.api import api_bp

app.register_blueprint(contact_bp)
app.register_blueprint(api_bp)
app.register_blueprint(seo_bp)


# Custom template filters
@app.template_filter("datetime")
def datetime_filter(datetime_obj, format="%Y-%m-%d %H:%M"):
    """Custom datetime filter for templates"""
    if datetime_obj is None:
        return "N/A"
    try:
        return datetime_obj.strftime(format)
    except (AttributeError, ValueError):
        return str(datetime_obj)


@app.template_filter("date")
def date_filter(date_obj, format="%Y-%m-%d"):
    """Custom date filter for templates"""
    if date_obj is None:
        return "N/A"
    try:
        return date_obj.strftime(format)
    except (AttributeError, ValueError):
        return str(date_obj)


# Template globals
@app.template_global()
def current_date():
    """Get current date for templates"""
    from datetime import datetime

    return datetime.now()


@app.template_global()
def default_data():
    """Provide default data structure for templates"""
    return {
        "users": {"total": 0, "growth_rate": 0, "new_today": 0},
        "seo": {"total_analyses": 0, "analyses_today": 0, "avg_score": 0},
        "leads": {"total_contacts": 0, "new_today": 0, "conversion_rate": 0},
        "system": {"redis_available": True, "cache_hit_rate": 95},
        "recent_activities": [],
        "posts": [],
        "pagination": None,
        "common_issues": [],
        "keywords": [],
        "issues": [],
    }


# Register tool blueprints


# ========================
# Database Test Route
# ========================
@app.route("/test-db")
def test_db():
    """Test database connectivity and show status"""
    try:
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        # Test user query
        try:
            user_count = User.query.count()
            user_status = f"✅ User table: {user_count} users"
        except Exception as e:
            user_status = f"❌ User table error: {str(e)}"

        # Test posts query
        try:
            post_count = Post.query.count()
            post_status = f"✅ Posts table: {post_count} posts"
        except Exception as e:
            post_status = f"❌ Posts table error: {str(e)}"

        return f"""
        <html>
        <head><title>Database Test</title></head>
        <body>
            <h1>Database Status</h1>
            <p><strong>Tables:</strong> {tables}</p>
            <p>{user_status}</p>
            <p>{post_status}</p>
            <br>
            <a href="/emergency-db-setup">Fix Database</a> | 
            <a href="/">Home</a> | 
            <a href="/users/login">Login</a>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <body>
            <h1>Database Error</h1>
            <p>Error: {str(e)}</p>
            <a href="/emergency-db-setup">Fix Database</a>
        </body>
        </html>
        """


# ========================
# Emergency Database Setup Route
# ========================
@app.route("/emergency-db-setup")
def emergency_db_setup():
    """Emergency database setup - accessible without login"""
    try:
        # Check if database needs setup
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        if "user" not in tables:
            needs_setup = True
            message = "Database tables don't exist"
        else:
            try:
                columns = [col["name"] for col in inspector.get_columns("user")]
                if "role" not in columns:
                    needs_setup = True
                    message = "User table missing 'role' column"
                else:
                    needs_setup = False
                    message = "Database appears to be properly configured"
            except:
                needs_setup = True
                message = "Error checking user table structure"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Emergency Database Setup</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                .status {{ padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .error {{ background: #f8d7da; color: #721c24; }}
                .success {{ background: #d4edda; color: #155724; }}
                .warning {{ background: #fff3cd; color: #856404; }}
            </style>
        </head>
        <body>
            <h1>🛠️ Emergency Database Setup</h1>
            <div class="status {'error' if needs_setup else 'success'}">
                <strong>Status:</strong> {message}
            </div>
            
            {'<button class="btn" onclick="fixDatabase()">Fix Database Now</button>' if needs_setup else '<p>✅ Database is ready!</p>'}
            
            <div id="result"></div>
            
            <script>
                function fixDatabase() {{
                    document.getElementById('result').innerHTML = '<p>🔄 Fixing database...</p>';
                    fetch('/emergency-db-fix', {{method: 'POST'}})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            document.getElementById('result').innerHTML = 
                                '<div class="status success">✅ ' + data.message + 
                                '<br><br><strong>Login with:</strong><br>Username: admin<br>Password: admin123<br><br>' +
                                '<a href="/users/login">Go to Login</a></div>';
                        }} else {{
                            document.getElementById('result').innerHTML = 
                                '<div class="status error">❌ Error: ' + data.message + '</div>';
                        }}
                    }});
                }}
            </script>
        </body>
        </html>
        """

    except Exception as e:
        return f"""
        <html>
        <body>
            <h1>Database Setup Error</h1>
            <p>Error: {str(e)}</p>
            <p>Try restarting the application.</p>
        </body>
        </html>
        """


@app.route("/emergency-db-fix", methods=["POST"])
def emergency_db_fix():
    """Emergency database fix endpoint"""
    try:
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()

        # Import all models to ensure they're all registered
        from users.models.user import User
        from users.models.order import Order
        from users.models.download import Download
        from admin.models import Setting
        from models.post import Post
        from models.contact import ContactMessage
        from models.newsletter import Subscriber
        from models.subscription import UserSubscription

        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@superseotoolkit.com",
            role="admin",
            is_active=True,
            email_verified=True,
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)

        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            role="customer",
            is_active=True,
            email_verified=True,
        )
        test_user.set_password("test123")
        db.session.add(test_user)

        # Create basic settings
        settings = [
            Setting(key="site_name", value="Super SEO Toolkit"),
            Setting(key="admin_email", value="admin@superseotoolkit.com"),
            Setting(key="maintenance_mode", value="false"),
            Setting(key="debug_mode", value="true"),
        ]
        for setting in settings:
            db.session.add(setting)

        # Create a sample post
        sample_post = Post(
            title="Welcome to Super SEO Toolkit",
            slug="welcome-to-super-seo-toolkit",
            content="This is a sample blog post to demonstrate the SEO toolkit functionality.",
            excerpt="Welcome post for the SEO toolkit",
            author_name="Admin",
            status="published",
        )
        db.session.add(sample_post)

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Database fixed successfully! Admin user and sample data created.",
            }
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"success": False, "message": f"Database fix failed: {str(e)}"}),
            500,
        )


# ========================
# Database Setup Route (Emergency)
# ========================
@app.route("/database-setup")
def database_setup_redirect():
    """Redirect to admin database setup"""
    return redirect(url_for("admin_system.database_setup"))


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
    # Try to fetch recent posts from database with error handling
    recent_posts = []
    try:
        recent_posts_db = Post.query.order_by(Post.created_at.desc()).limit(3).all()
        # Format posts for template: add image URL using url_for static path
        for post in recent_posts_db:
            recent_posts.append(
                {
                    "title": post.title,
                    "slug": post.slug,
                    "summary": post.excerpt or (post.content[:120] + "..."),
                    "image": post.featured_image,
                }
            )
    except Exception as e:
        # If posts table doesn't exist or has issues, use empty list
        current_app.logger.warning(f"Could not fetch posts: {e}")
        recent_posts = []

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
# Context Processors
# ========================
@app.context_processor
def ads_context():
    """Context processor to determine if ads should be displayed"""

    def should_show_ads():
        try:
            # Check if AdSense is approved
            adsense_approved = (
                os.getenv("GOOGLE_ADSENSE_APPROVED", "false").lower() == "true"
            )
            if not adsense_approved:
                return False

            # Check if we're on an allowed page (tools pages and other general pages)
            # Exclude: homepage, admin pages, user pages
            excluded_endpoints = [
                "home",
                "index",  # Homepage
                "admin.",  # Admin pages
                "users.",  # User pages
                "auth.",  # Auth pages
            ]

            is_excluded_page = False
            if request.endpoint:
                for excluded in excluded_endpoints:
                    if request.endpoint == excluded or request.endpoint.startswith(
                        excluded
                    ):
                        is_excluded_page = True
                        break

            # Also exclude if URL contains these paths
            excluded_paths = [
                "/admin/",
                "/users/",
                "/user/",
                "/login",
                "/register",
                "/logout",
            ]
            is_excluded_url = any(path in request.path for path in excluded_paths)

            if is_excluded_page or is_excluded_url or request.path == "/":
                return False

            # Check user subscription status
            if current_user.is_authenticated:
                try:
                    # Check if user has active premium subscription
                    from models.subscription import UserSubscription
                    from datetime import datetime

                    active_subscription = UserSubscription.query.filter(
                        UserSubscription.user_id == current_user.id,
                        UserSubscription.status == "active",
                        UserSubscription.end_date > datetime.utcnow(),
                    ).first()

                    is_premium_user = (
                        current_user.is_premium or active_subscription is not None
                    )
                    return not is_premium_user  # Show ads only to non-premium users
                except Exception:
                    # If there's an error checking subscription, default to showing ads
                    return not getattr(current_user, "is_premium", False)
            else:
                return True  # Non-authenticated users see ads

        except Exception:
            # If there's any error, default to not showing ads for safety
            return False

    def get_adsense_config():
        """Get AdSense configuration"""
        try:
            return {
                "client_id": os.getenv("GOOGLE_ADSENSE_CLIENT_ID", ""),
                "approved": os.getenv("GOOGLE_ADSENSE_APPROVED", "false").lower()
                == "true",
                "sidebar_slot": os.getenv("ADSENSE_SIDEBAR_SLOT", ""),
                "bottom_slot": os.getenv("ADSENSE_BOTTOM_SLOT", ""),
            }
        except Exception:
            # Return safe defaults if there's an error
            return {
                "client_id": "",
                "approved": False,
                "sidebar_slot": "",
                "bottom_slot": "",
            }

    return dict(should_show_ads=should_show_ads, get_adsense_config=get_adsense_config)


# ========================
# Other Static Pages
# ========================
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

if __name__ == "__main__":
    with app.app_context():
        # from init_db import init_db
        # init_db()  # Initialize the database and default settings
        pass

    app.run(debug=False, host="0.0.0.0", port=5000)
