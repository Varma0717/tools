import os
import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash

from app.models.post import Post
from app.models.newsletter import Newsletter, Subscriber
from app.models.testimonial import Testimonial
from app.models.faq import FAQ
from app.core.extensions import db, csrf

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Homepage route with full functionality."""
    try:
        # Try to get recent blog posts
        recent_posts = []
        try:
            posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
            for post in posts:
                recent_posts.append(
                    {
                        "title": post.title,
                        "slug": post.slug,
                        "summary": post.summary or (post.content[:120] + "..."),
                        "image": post.image,
                    }
                )
        except Exception as e:
            # Fallback to static data if database issues
            print(f"⚠️  Database query failed, using static data: {e}")
            recent_posts = [
                {
                    "title": "Complete Guide to Technical SEO in 2025",
                    "slug": "complete-guide-technical-seo-2025",
                    "summary": "Master technical SEO with our comprehensive guide covering Core Web Vitals, structured data, and advanced optimization techniques.",
                    "image": None,
                },
                {
                    "title": "AI-Powered SEO: The Future of Content Optimization",
                    "slug": "ai-powered-seo-content-optimization",
                    "summary": "Discover how artificial intelligence is transforming SEO and learn to leverage AI tools for better rankings and content performance.",
                    "image": None,
                },
                {
                    "title": "Local SEO Strategies That Actually Work",
                    "slug": "local-seo-strategies-that-work",
                    "summary": "Boost your local search presence with proven strategies for Google My Business optimization, local citations, and geo-targeted content.",
                    "image": None,
                },
            ]

        # Get testimonials for corporate homepage
        testimonials = []
        try:
            testimonials_query = Testimonial.query.limit(3).all()
            for testimonial in testimonials_query:
                testimonials.append(
                    {
                        "author": testimonial.author,
                        "company": testimonial.company,
                        "content": testimonial.content,
                        "rating": testimonial.rating or 5,
                    }
                )
        except Exception as e:
            print(f"⚠️  Testimonials query failed, using static data: {e}")
            testimonials = [
                {
                    "author": "Sarah Johnson",
                    "company": "TechCorp",
                    "content": "This platform has revolutionized our SEO workflow. The accuracy and speed of analysis is incredible.",
                    "rating": 5,
                },
                {
                    "author": "Michael Chen",
                    "company": "Growth Agency",
                    "content": "The freemium model is perfect. We started free and upgraded when we needed advanced features.",
                    "rating": 5,
                },
                {
                    "author": "Alex Rodriguez",
                    "company": "Digital Solutions Inc",
                    "content": "Comprehensive tools with enterprise-level security. Exactly what our team needed.",
                    "rating": 5,
                },
            ]

        # FAQs data
        faqs = []
        try:
            faqs = FAQ.query.limit(6).all()
        except Exception as e:
            print(f"⚠️  FAQs query failed, using static data: {e}")
            faqs = [
                {
                    "question": "How accurate are the SEO audit results?",
                    "answer": "Our SEO audit tools use industry-standard algorithms and real-time data to provide highly accurate results. We analyze over 100+ SEO factors including technical issues, content optimization, and performance metrics.",
                    "updated_at": None,
                },
                {
                    "question": "Can I use the tools for multiple websites?",
                    "answer": "Yes! You can analyze unlimited websites with our tools. There are no restrictions on the number of domains you can audit, making it perfect for agencies and businesses managing multiple sites.",
                    "updated_at": None,
                },
                {
                    "question": "Do you store or share my website data?",
                    "answer": "We prioritize your privacy. We don't store your website data permanently and never share it with third parties. All analysis is done in real-time and data is deleted after processing.",
                    "updated_at": None,
                },
            ]

        # Static categories for the tool categories section
        categories = [
            {"name": "Technical SEO", "slug": "technical-seo"},
            {"name": "Content Optimization", "slug": "content-optimization"},
            {"name": "Performance Analysis", "slug": "performance-analysis"},
            {"name": "Keyword Research", "slug": "keyword-research"},
        ]

        return render_template(
            "home.html",
            recent_posts=recent_posts,
            testimonials=testimonials,
            faqs=faqs,
            categories=categories,
            tools_count=25,
            success_stories=2500,
        )

    except Exception as e:
        # If all else fails, return simple error message
        print(f"❌ Homepage error: {str(e)}")
        import traceback

        traceback.print_exc()
        return f"Homepage error: {str(e)}"


@main_bp.route("/test-simple")
def test_simple():
    """Simple test route without database or templates."""
    try:
        from flask import request

        print(f"🔍 Request method: {request.method}")
        print(f"🔍 Request headers: {dict(request.headers)}")
        print(f"🔍 Request remote_addr: {request.remote_addr}")
        print(f"🔍 Request user_agent: {request.user_agent}")
        return "Simple test works!"
    except Exception as e:
        print(f"❌ Error in test_simple: {e}")
        import traceback

        traceback.print_exc()
        return f"Error: {e}"


@main_bp.route("/test-template")
def test_template():
    """Test route with just template rendering."""
    try:
        return render_template("base.html")
    except Exception as e:
        return f"Template error: {str(e)}"


@main_bp.route("/debug-template")
def debug_template():
    """Debug template rendering step by step."""
    try:
        # Step 2: Test basic template rendering
        return render_template("base.html")
    except Exception as e:
        return f"Template error: {str(e)}"


@main_bp.route("/debug-home")
def debug_home():
    """Debug home template with minimal data."""
    try:
        # Step 3: Test home template with static data
        context = {
            "recent_posts": [
                {
                    "title": "Getting Started with SEO",
                    "slug": "getting-started-with-seo",
                    "summary": "Learn the basics of search engine optimization.",
                    "image": None,
                }
            ],
            "testimonials": [
                {
                    "name": "John Doe",
                    "company": "Tech Corp",
                    "text": "Great SEO tools!",
                    "image": None,
                }
            ],
            "tools_count": 25,
            "success_stories": 2500,
        }
        return render_template("home.html", **context)
    except Exception as e:
        return f"Home template error: {str(e)}"


@main_bp.route("/pricing")
def pricing():
    """Pricing page route."""
    from flask import current_app
    from flask_wtf.csrf import generate_csrf
    import os

    # Debug: Check template file modification time
    template_path = os.path.join(
        current_app.root_path, "..", "templates", "pricing.html"
    )
    if os.path.exists(template_path):
        mtime = os.path.getmtime(template_path)
        print(f"DEBUG: Template modified at: {mtime}")

    # Define pricing plans data - Corporate pricing structure
    plans = [
        {
            "title": "Starter",
            "price": "$0",
            "period": "forever",
            "desc": "Perfect for individuals and small projects getting started with professional SEO",
            "features": [
                "25+ Professional SEO Tools",
                "Website Performance Analysis",
                "Meta Tags & Schema Markup Validator",
                "Broken Link & SSL Certificate Checker",
                "DNS & WHOIS Domain Lookup",
                "Keyword Density Analysis",
                "Open Graph & Twitter Card Preview",
                "Basic Site Audit Reports",
                "PDF & Excel Export Options",
                "Community Support",
                "5 AI-Powered Tool Uses/Month",
            ],
            "button": "Get Started Free",
            "highlight": False,
            "plan_type": "free",
            "badge": None,
        },
        {
            "title": "Professional",
            "price": "$10",
            "period": "/month",
            "desc": "Ideal for marketing professionals, agencies, and growing businesses",
            "features": [
                "Everything in Starter Plan",
                "Unlimited AI Content Generator",
                "Advanced Content Rewriter & Optimizer",
                "Smart Headline & Meta Title Generator",
                "Comprehensive Technical SEO Audit",
                "Bulk URL Processing & Analysis",
                "Advanced Analytics & Insights Dashboard",
                "White-label PDF Reports",
                "Priority Email & Chat Support",
                "API Access for Integrations",
                "Advanced Keyword Research Tools",
                "Competitor Analysis Features",
                "Custom Reporting & Automation",
            ],
            "button": "Upgrade to Professional",
            "highlight": True,
            "plan_type": "pro",
            "badge": "Most Popular",
        },
        {
            "title": "Enterprise",
            "price": "Custom",
            "period": "contact us",
            "desc": "Tailored solutions for large organizations with advanced SEO requirements",
            "features": [
                "Everything in Professional Plan",
                "Dedicated Account Manager",
                "Custom Tool Development",
                "Enterprise-grade Security & Compliance",
                "Advanced Team Management & Permissions",
                "Custom Integrations & API Limits",
                "Advanced Workflow Automation",
                "White-label Platform Branding",
                "SLA with 99.9% Uptime Guarantee",
                "24/7 Phone & Priority Support",
                "Advanced Training & Onboarding",
                "Custom Reporting & Analytics",
                "Dedicated Infrastructure Options",
            ],
            "button": "Contact Sales",
            "highlight": False,
            "plan_type": "enterprise",
            "badge": "Enterprise",
        },
    ]

    context = {
        "plans": plans,
        "paypal_client_id": current_app.config.get("PAYPAL_CLIENT_ID"),
        "paypal_environment": current_app.config.get("PAYPAL_ENVIRONMENT", "sandbox"),
        "stripe_publishable_key": current_app.config.get("STRIPE_PUBLISHABLE_KEY"),
        "csrf_token": generate_csrf(),
        "debug_plans_count": len(plans),
        "debug_timestamp": str(os.time.time() if hasattr(os, "time") else "unknown"),
    }

    print(f"DEBUG: Rendering pricing.html with {len(plans)} plans")
    return render_template("pricing.html", **context)


@main_bp.route("/about")
def about():
    """About page route."""
    return render_template("about.html")


@main_bp.route("/privacy")
def privacy():
    """Privacy policy page route."""
    return render_template("privacy.html")


@main_bp.route("/terms")
def terms():
    """Terms of service page route."""
    return render_template("terms.html")


@main_bp.route("/cookies")
def cookies():
    """Cookie policy page route."""
    return render_template("cookies.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact page route with form handling."""
    if request.method == "POST":
        try:
            # Get form data
            data = request.get_json() if request.is_json else request.form

            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            subject = data.get("subject", "").strip()
            message = data.get("message", "").strip()

            # Validation
            if not all([name, email, subject, message]):
                return (
                    jsonify({"success": False, "message": "All fields are required."}),
                    400,
                )

            # Email validation
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Please enter a valid email address.",
                        }
                    ),
                    400,
                )

            # Save to database
            from app.models.contact import Contact

            contact_message = Contact(
                name=name, email=email, subject=subject, message=message
            )
            db.session.add(contact_message)
            db.session.commit()

            # Send emails
            from app.services.email_service import EmailService

            contact_data = {
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
            }

            # Send notification to admin
            admin_sent = EmailService.send_contact_notification(contact_data)

            # Send confirmation to user
            user_sent = EmailService.send_contact_confirmation(email, name)

            if admin_sent or user_sent:
                return jsonify(
                    {
                        "success": True,
                        "message": "Thank you for your message! We'll get back to you soon.",
                    }
                )
            else:
                return jsonify(
                    {
                        "success": True,
                        "message": "Your message has been saved. We'll get back to you soon.",
                    }
                )

        except Exception as e:
            db.session.rollback()
            print(f"Contact form error: {str(e)}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "An error occurred. Please try again later.",
                    }
                ),
                500,
            )

    return render_template("contact.html")


@main_bp.route("/newsletter/subscribe", methods=["POST"])
@csrf.exempt
def newsletter_subscribe():
    """Handle newsletter subscription."""
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get("email", "").strip()

        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not email or not re.match(email_pattern, email):
            return (
                jsonify(
                    {"success": False, "message": "Please enter a valid email address."}
                ),
                400,
            )

        # Check if subscriber already exists
        existing_subscriber = Subscriber.query.filter_by(email=email).first()
        if existing_subscriber:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "You're already subscribed to our newsletter.",
                    }
                ),
                400,
            )

        # Create new subscriber
        subscriber = Subscriber(email=email, is_active=True)
        db.session.add(subscriber)
        db.session.commit()

        # Send welcome email
        from app.services.email_service import EmailService

        EmailService.send_newsletter_welcome(email)

        return jsonify(
            {"success": True, "message": "Thank you for subscribing to our newsletter!"}
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An error occurred. Please try again later.",
                }
            ),
            500,
        )


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page - redirect to auth register"""
    return redirect(url_for("auth.register"))


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login page - redirect to auth login"""
    return redirect(url_for("auth.login"))


@main_bp.route("/testimonials")
def testimonials():
    """Testimonials page"""
    try:
        # Get all testimonials from database
        testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
        return render_template("testimonials.html", testimonials=testimonials)
    except Exception as e:
        print(f"⚠️  Testimonials query failed: {e}")
        # Fallback data
        testimonials = [
            {
                "author": "Sarah Johnson",
                "company": "TechCorp",
                "position": "CEO",
                "content": "This platform has revolutionized our SEO workflow. The accuracy and speed of analysis is incredible.",
                "rating": 5,
            },
            {
                "author": "Michael Chen",
                "company": "Growth Agency",
                "position": "SEO Manager",
                "content": "The freemium model is perfect. We started free and upgraded when we needed advanced features.",
                "rating": 5,
            },
        ]
        return render_template("testimonials.html", testimonials=testimonials)


@main_bp.route("/faq")
def faq():
    """FAQ page"""
    try:
        # Get all FAQs from database, ordered by position and featured status
        faqs = FAQ.query.order_by(FAQ.featured.desc(), FAQ.order_position.asc()).all()

        # Group FAQs by category
        faq_categories = {}
        for faq_item in faqs:
            category = faq_item.category or "General"
            if category not in faq_categories:
                faq_categories[category] = []
            faq_categories[category].append(faq_item)

        return render_template("faq.html", faq_categories=faq_categories, faqs=faqs)
    except Exception as e:
        print(f"⚠️  FAQ query failed: {e}")
        # Fallback data
        faqs = [
            {
                "question": "How accurate are the SEO audit results?",
                "answer": "Our SEO audit tools use industry-standard algorithms and real-time data to provide highly accurate results.",
                "category": "General",
            },
            {
                "question": "Can I use the tools for multiple websites?",
                "answer": "Yes! You can analyze unlimited websites with our tools.",
                "category": "General",
            },
        ]
        faq_categories = {"General": faqs}
        return render_template("faq.html", faq_categories=faq_categories, faqs=faqs)


@main_bp.route("/checkout")
def checkout():
    """Checkout page for subscription payments"""
    plan = request.args.get("plan", "professional")
    billing = request.args.get("billing", "monthly")

    # Validate plan
    valid_plans = ["free", "professional"]
    if plan not in valid_plans:
        flash("Invalid plan selected", "error")
        return redirect(url_for("main.pricing"))

    # Free plan doesn't need checkout
    if plan == "free":
        flash("Free plan is already active", "info")
        return redirect(url_for("main.index"))

    return render_template("checkout.html", plan=plan, billing=billing)


@main_bp.route("/payment/success")
def payment_success():
    """Payment success page"""
    payment_id = request.args.get("payment_id")

    if not payment_id:
        flash("Payment information not found", "error")
        return redirect(url_for("main.index"))

    return render_template("payment_success.html", payment_id=payment_id)
