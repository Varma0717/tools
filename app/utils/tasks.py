"""
Background task management using Celery.
"""

import os
from datetime import datetime
from flask import current_app
from app.core.extensions import db, mail
from flask_mail import Message

try:
    from celery import Celery

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

    # Create a dummy Celery class for when Celery is not available
    class Celery:
        def __init__(self, *args, **kwargs):
            pass

        def task(self, *args, **kwargs):
            def decorator(func):
                # Return the function as-is when Celery is not available
                return func

            return decorator


def make_celery(app):
    """Create Celery instance."""
    if not CELERY_AVAILABLE:
        return None

    celery = Celery(
        app.import_name,
        backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
        broker=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    )

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# Initialize Celery (will be configured in app factory)
if CELERY_AVAILABLE:
    celery = Celery(__name__)
else:
    # Create a dummy celery instance
    class DummyCelery:
        def task(self, *args, **kwargs):
            def decorator(func):
                # Add a .delay method to functions for compatibility
                def delay_method(*args, **kwargs):
                    # Execute immediately when Celery is not available
                    return func(*args, **kwargs)

                func.delay = delay_method
                return func

            return decorator

    celery = DummyCelery()


@celery.task
def send_async_email(email_data):
    """Send email asynchronously."""
    try:
        msg = Message(
            subject=email_data["subject"],
            recipients=email_data["recipients"],
            html=email_data.get("html"),
            body=email_data.get("body"),
        )
        mail.send(msg)
        return {"status": "sent", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery.task
def process_bulk_operation(operation_type, data):
    """Process bulk operations asynchronously."""
    try:
        if operation_type == "bulk_email":
            results = []
            for email_item in data:
                result = send_async_email.delay(email_item)
                results.append(result.id)
            return {"status": "queued", "task_ids": results}

        elif operation_type == "data_export":
            # Handle data export
            from models import User, Post  # Import here to avoid circular imports

            export_data = []
            if data.get("model") == "users":
                users = User.query.all()
                export_data = [user.to_dict() for user in users]
            elif data.get("model") == "posts":
                posts = Post.query.all()
                export_data = [post.to_dict() for post in posts]

            # Save to file or cloud storage
            filename = f"export_{operation_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            # Implementation for saving export data

            return {
                "status": "completed",
                "filename": filename,
                "records": len(export_data),
            }

        return {"status": "unknown_operation", "operation": operation_type}

    except Exception as e:
        return {"status": "failed", "error": str(e)}


@celery.task
def cleanup_old_data():
    """Clean up old data periodically."""
    try:
        from app.models.page_view import PageView
        from datetime import timedelta

        # Delete page views older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        old_views = PageView.query.filter(PageView.created_at < cutoff_date).all()

        for view in old_views:
            db.session.delete(view)

        db.session.commit()

        return {"status": "completed", "deleted_records": len(old_views)}

    except Exception as e:
        return {"status": "failed", "error": str(e)}


@celery.task
def generate_sitemap():
    """Generate sitemap asynchronously."""
    try:
        from app.models.post import Post
        from flask import url_for
        import xml.etree.ElementTree as ET

        # Create sitemap XML
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

        # Add homepage
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = current_app.config.get(
            "SITE_URL", "http://localhost:5000"
        )
        ET.SubElement(url, "changefreq").text = "daily"
        ET.SubElement(url, "priority").text = "1.0"

        # Add blog posts
        posts = Post.query.filter_by(published=True).all()
        for post in posts:
            url = ET.SubElement(urlset, "url")
            ET.SubElement(url, "loc").text = (
                f"{current_app.config.get('SITE_URL')}/blog/{post.slug}"
            )
            ET.SubElement(url, "lastmod").text = post.updated_at.strftime("%Y-%m-%d")
            ET.SubElement(url, "changefreq").text = "monthly"
            ET.SubElement(url, "priority").text = "0.8"

        # Save sitemap
        tree = ET.ElementTree(urlset)
        sitemap_path = "static/sitemap.xml"
        tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)

        return {"status": "completed", "file": sitemap_path, "urls": len(posts) + 1}

    except Exception as e:
        return {"status": "failed", "error": str(e)}
