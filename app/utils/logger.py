import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging():
    """
    Setup comprehensive logging system with file rotation and size limits
    """
    # Create logs directory if it doesn't exist (project root level)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure main application logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)

    # Clear existing handlers to avoid duplicates
    app_logger.handlers.clear()

    # File handler with rotation (10MB max, keep 5 backup files)
    app_log_file = os.path.join(logs_dir, "app.log")
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )

    # Console handler for development
    console_handler = logging.StreamHandler()

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S"
    )

    # Set formatters
    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)

    # Add handlers to logger
    app_logger.addHandler(file_handler)
    app_logger.addHandler(console_handler)

    # Setup SEO audit specific logger
    seo_logger = logging.getLogger("seo_audit")
    seo_logger.setLevel(logging.INFO)

    # SEO audit log file with rotation
    seo_log_file = os.path.join(logs_dir, "seo_audit.log")
    seo_file_handler = logging.handlers.RotatingFileHandler(
        seo_log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"  # 5MB
    )
    seo_file_handler.setFormatter(detailed_formatter)
    seo_logger.addHandler(seo_file_handler)

    # Setup error logger for critical issues
    error_logger = logging.getLogger("errors")
    error_logger.setLevel(logging.ERROR)

    error_log_file = os.path.join(logs_dir, "errors.log")
    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=10,
        encoding="utf-8",
    )
    error_file_handler.setFormatter(detailed_formatter)
    error_logger.addHandler(error_file_handler)

    # Setup user activity logger
    activity_logger = logging.getLogger("user_activity")
    activity_logger.setLevel(logging.INFO)

    activity_log_file = os.path.join(logs_dir, "user_activity.log")
    activity_file_handler = logging.handlers.RotatingFileHandler(
        activity_log_file,
        maxBytes=8 * 1024 * 1024,  # 8MB
        backupCount=7,
        encoding="utf-8",
    )
    activity_file_handler.setFormatter(detailed_formatter)
    activity_logger.addHandler(activity_file_handler)

    print(f"Logging system initialized. Log files will be saved to: {logs_dir}")

    return {
        "app": app_logger,
        "seo_audit": seo_logger,
        "errors": error_logger,
        "user_activity": activity_logger,
    }


def log_seo_audit(user_id, url, score, analysis_type="full"):
    """Log SEO audit activity"""
    logger = logging.getLogger("seo_audit")
    logger.info(
        f"SEO Audit | User: {user_id} | URL: {url} | Score: {score} | Type: {analysis_type}"
    )


def log_user_activity(user_id, action, details=None):
    """Log user activity"""
    logger = logging.getLogger("user_activity")
    details_str = f" | Details: {details}" if details else ""
    logger.info(f"User Activity | User: {user_id} | Action: {action}{details_str}")


def log_error(error_type, message, user_id=None, additional_info=None):
    """Log application errors"""
    logger = logging.getLogger("errors")
    user_str = f" | User: {user_id}" if user_id else ""
    info_str = f" | Info: {additional_info}" if additional_info else ""
    logger.error(f"Error | Type: {error_type} | Message: {message}{user_str}{info_str}")


def log_app_info(message):
    """Log general application information"""
    logger = logging.getLogger("app")
    logger.info(message)


def log_app_warning(message):
    """Log application warnings"""
    logger = logging.getLogger("app")
    logger.warning(message)


def cleanup_old_logs():
    """
    Clean up log files older than 30 days
    This should be called periodically (e.g., daily cron job)
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    logs_dir = os.path.join(project_root, "logs")
    if not os.path.exists(logs_dir):
        return

    cutoff_time = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30 days ago

    for filename in os.listdir(logs_dir):
        file_path = os.path.join(logs_dir, filename)
        if os.path.isfile(file_path):
            file_modified = os.path.getmtime(file_path)
            if file_modified < cutoff_time:
                try:
                    os.remove(file_path)
                    print(f"Removed old log file: {filename}")
                except OSError as e:
                    print(f"Error removing log file {filename}: {e}")


# Test the logging system
def test_logging_system():
    """Test the logging system"""
    loggers = setup_logging()

    # Test different log levels and loggers
    log_app_info("Application started successfully")
    log_user_activity(123, "login", "successful login from IP 192.168.1.1")
    log_seo_audit(123, "https://example.com", 85, "premium")
    log_error(
        "ValidationError",
        "Invalid URL provided",
        user_id=123,
        additional_info="URL: invalid-url",
    )
    log_app_warning("Rate limit approaching for user 123")

    print("Logging system test completed. Check logs/ directory for output files.")


if __name__ == "__main__":
    test_logging_system()
