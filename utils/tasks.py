"""
Background Task Processing with Celery
Handles async operations for Super SEO Toolkit
"""

import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
import json
import requests
from celery import Celery
from flask import current_app
from utils.extensions import db
from models.newsletter import Subscriber
from models.contact import ContactMessage as Contact
from models.post import Post


# Initialize Celery
def make_celery(app=None):
    """Create Celery instance"""
    celery = Celery(
        "seo_toolkit",
        broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1"),
        backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
        include=["utils.tasks"],
    )

    # Configure Celery
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        result_expires=3600,  # 1 hour
        beat_schedule={
            "cleanup-expired-sessions": {
                "task": "utils.tasks.cleanup_expired_sessions",
                "schedule": 3600.0,  # Every hour
            },
            "generate-daily-reports": {
                "task": "utils.tasks.generate_daily_reports",
                "schedule": 86400.0,  # Daily
            },
            "cleanup-old-logs": {
                "task": "utils.tasks.cleanup_old_logs",
                "schedule": 604800.0,  # Weekly
            },
            "update-seo-metrics": {
                "task": "utils.tasks.update_seo_metrics",
                "schedule": 3600.0,  # Every hour
            },
        },
    )

    if app:

        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context."""

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# Create Celery instance (will be initialized with app context)
celery = make_celery()


@celery.task(bind=True, max_retries=3)
def send_email_async(
    self,
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = None,
    from_email: str = None,
):
    """
    Send email asynchronously with retry logic

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email content
        text_content: Plain text content (optional)
        from_email: Sender email (optional)
    """
    try:
        from flask import current_app

        # Email configuration
        smtp_server = current_app.config.get("MAIL_SERVER", "localhost")
        smtp_port = current_app.config.get("MAIL_PORT", 587)
        smtp_username = current_app.config.get("MAIL_USERNAME")
        smtp_password = current_app.config.get("MAIL_PASSWORD")
        smtp_use_tls = current_app.config.get("MAIL_USE_TLS", True)

        sender_email = from_email or current_app.config.get("MAIL_DEFAULT_SENDER")

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        # Add text content
        if text_content:
            text_part = MIMEText(text_content, "plain")
            msg.attach(text_part)

        # Add HTML content
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_use_tls:
                server.starttls()

            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)

            server.send_message(msg)

        return {
            "status": "success",
            "message": f"Email sent to {to_email}",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        # Retry with exponential backoff
        countdown = 2**self.request.retries * 60  # 1min, 2min, 4min

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=countdown)

        # Log final failure
        current_app.logger.error(f"Failed to send email to {to_email}: {exc}")

        return {
            "status": "failed",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery.task(bind=True)
def send_newsletter_batch(self, newsletter_id: int, recipient_batch: List[str]):
    """
    Send newsletter to a batch of recipients

    Args:
        newsletter_id: Newsletter ID
        recipient_batch: List of email addresses
    """
    try:
        from utils.extensions import db

        newsletter = db.session.get(Subscriber, newsletter_id)
        if not newsletter:
            return {"status": "failed", "error": "Newsletter not found"}

        results = []

        for email in recipient_batch:
            try:
                # Send individual email
                result = send_email_async.delay(
                    to_email=email,
                    subject=newsletter.subject,
                    html_content=newsletter.html_content,
                    text_content=newsletter.text_content,
                )

                results.append(
                    {"email": email, "task_id": result.id, "status": "queued"}
                )

            except Exception as e:
                results.append({"email": email, "status": "failed", "error": str(e)})

        return {
            "status": "completed",
            "batch_size": len(recipient_batch),
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        current_app.logger.error(f"Newsletter batch send failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery.task
def generate_seo_report(url: str, user_id: int, report_type: str = "full"):
    """
    Generate comprehensive SEO report for a URL

    Args:
        url: Target URL to analyze
        user_id: User requesting the report
        report_type: Type of report ('full', 'basic', 'technical')
    """
    try:
        from tools.utils.seo_analyzer import SEOAnalyzer
        from models.post import Post

        # Initialize SEO analyzer
        analyzer = SEOAnalyzer()

        # Perform SEO analysis
        report_data = {
            "url": url,
            "user_id": user_id,
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "analysis": {},
        }

        # Basic SEO checks
        if report_type in ["full", "basic"]:
            report_data["analysis"].update(
                {
                    "meta_tags": analyzer.analyze_meta_tags(url),
                    "headings": analyzer.analyze_headings(url),
                    "images": analyzer.analyze_images(url),
                    "links": analyzer.analyze_links(url),
                }
            )

        # Technical SEO checks
        if report_type in ["full", "technical"]:
            report_data["analysis"].update(
                {
                    "page_speed": analyzer.analyze_page_speed(url),
                    "mobile_friendly": analyzer.check_mobile_friendly(url),
                    "ssl_certificate": analyzer.check_ssl(url),
                    "sitemap": analyzer.check_sitemap(url),
                }
            )

        # Full analysis includes everything
        if report_type == "full":
            report_data["analysis"].update(
                {
                    "content_quality": analyzer.analyze_content_quality(url),
                    "social_signals": analyzer.analyze_social_signals(url),
                    "local_seo": analyzer.analyze_local_seo(url),
                    "competitors": analyzer.analyze_competitors(url),
                }
            )

        # Save report to database (optional)
        if current_app.config.get("SAVE_SEO_REPORTS", True):
            # Create blog post with report
            post = Post(
                title=f"SEO Report for {url}",
                content=json.dumps(report_data, indent=2),
                author_id=user_id,
                category_id=1,  # SEO Reports category
                is_published=False,  # Private report
                meta_description=f"Comprehensive SEO analysis for {url}",
            )

            db.session.add(post)
            db.session.commit()

            report_data["post_id"] = post.id

        return {
            "status": "completed",
            "report": report_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        current_app.logger.error(f"SEO report generation failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery.task
def process_bulk_urls(urls: List[str], user_id: int, tool_name: str):
    """
    Process multiple URLs with specified SEO tool

    Args:
        urls: List of URLs to process
        user_id: User ID
        tool_name: Name of the SEO tool to use
    """
    try:
        results = []

        for url in urls:
            try:
                # Import tool dynamically based on tool_name
                if tool_name == "meta_tag_analyzer":
                    from tools.utils.meta_analyzer import analyze_meta_tags

                    result = analyze_meta_tags(url)
                elif tool_name == "broken_link_checker":
                    from tools.utils.link_checker import check_broken_links

                    result = check_broken_links(url)
                elif tool_name == "page_speed_tester":
                    from tools.utils.speed_tester import test_page_speed

                    result = test_page_speed(url)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                results.append({"url": url, "result": result, "status": "completed"})

            except Exception as e:
                results.append({"url": url, "error": str(e), "status": "failed"})

        return {
            "status": "completed",
            "tool_name": tool_name,
            "user_id": user_id,
            "total_urls": len(urls),
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        current_app.logger.error(f"Bulk URL processing failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery.task
def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    try:
        from utils.caching import cache_manager

        # Clean up expired cache entries
        expired_count = 0

        # This would require Redis SCAN for pattern matching
        # For now, we'll implement basic cleanup

        return {
            "status": "completed",
            "cleaned_sessions": expired_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        current_app.logger.error(f"Session cleanup failed: {exc}")
        return {"status": "failed", "error": str(exc)}


@celery.task
def generate_daily_reports():
    """Generate daily analytics reports"""
    try:
        from models.page_view import PageView
        from models.post import Post
        from datetime import date

        today = date.today()
        yesterday = today - timedelta(days=1)

        # Get page views for yesterday
        page_views = PageView.query.filter(
            PageView.timestamp >= yesterday, PageView.timestamp < today
        ).count()

        # Get new posts
        new_posts = Post.query.filter(
            Post.created_at >= yesterday, Post.created_at < today
        ).count()

        # Get new contacts
        new_contacts = Contact.query.filter(
            Contact.created_at >= yesterday, Contact.created_at < today
        ).count()

        report_data = {
            "date": yesterday.isoformat(),
            "page_views": page_views,
            "new_posts": new_posts,
            "new_contacts": new_contacts,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Save or send report
        # Implementation depends on requirements

        return {"status": "completed", "report": report_data}

    except Exception as exc:
        current_app.logger.error(f"Daily report generation failed: {exc}")
        return {"status": "failed", "error": str(exc)}


@celery.task
def cleanup_old_logs():
    """Clean up old log files"""
    try:
        import glob

        log_dir = current_app.config.get("LOG_DIR", "logs")
        retention_days = current_app.config.get("LOG_RETENTION_DAYS", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        cleaned_files = 0

        # Clean up old log files
        for log_file in glob.glob(os.path.join(log_dir, "*.log.*")):
            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_mtime < cutoff_date:
                    os.remove(log_file)
                    cleaned_files += 1
            except OSError:
                continue

        return {
            "status": "completed",
            "cleaned_files": cleaned_files,
            "retention_days": retention_days,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        current_app.logger.error(f"Log cleanup failed: {exc}")
        return {"status": "failed", "error": str(exc)}


@celery.task
def update_seo_metrics():
    """Update SEO metrics for tracked URLs"""
    try:
        # This would integrate with SEO APIs to update metrics
        # Implementation depends on which SEO tools/APIs are used

        updated_metrics = 0

        # Placeholder for SEO metrics update logic
        # Could integrate with Google Search Console API,
        # SEMrush API, Ahrefs API, etc.

        return {
            "status": "completed",
            "updated_metrics": updated_metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        current_app.logger.error(f"SEO metrics update failed: {exc}")
        return {"status": "failed", "error": str(exc)}


# Utility functions for task management


def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a Celery task"""
    try:
        result = celery.AsyncResult(task_id)

        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "info": result.info,
            "successful": result.successful() if result.ready() else None,
            "failed": result.failed() if result.ready() else None,
        }

    except Exception as e:
        return {"task_id": task_id, "status": "ERROR", "error": str(e)}


def cancel_task(task_id: str) -> bool:
    """Cancel a Celery task"""
    try:
        celery.control.revoke(task_id, terminate=True)
        return True
    except Exception:
        return False


def get_active_tasks() -> List[Dict[str, Any]]:
    """Get list of active tasks"""
    try:
        inspect = celery.control.inspect()
        active_tasks = inspect.active()

        if active_tasks:
            all_tasks = []
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    all_tasks.append(
                        {
                            "worker": worker,
                            "task_id": task["id"],
                            "name": task["name"],
                            "args": task["args"],
                            "kwargs": task["kwargs"],
                            "time_start": task.get("time_start"),
                        }
                    )
            return all_tasks

        return []

    except Exception as e:
        current_app.logger.error(f"Failed to get active tasks: {e}")
        return []
