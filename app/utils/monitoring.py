"""
Advanced logging and monitoring system.
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional
from flask import request, g, current_app
from logging.handlers import RotatingFileHandler, SMTPHandler
import threading


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""

    def __init__(self):
        self.metrics = {}
        self.requests = []
        self.errors = []
        self.lock = threading.Lock()

    def record_request(
        self, endpoint: str, method: str, duration: float, status_code: int
    ):
        """Record request metrics."""
        with self.lock:
            key = f"{method}:{endpoint}"
            if key not in self.metrics:
                self.metrics[key] = {
                    "count": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "min_time": float("inf"),
                    "max_time": 0,
                    "status_codes": {},
                }

            metrics = self.metrics[key]
            metrics["count"] += 1
            metrics["total_time"] += duration
            metrics["avg_time"] = metrics["total_time"] / metrics["count"]
            metrics["min_time"] = min(metrics["min_time"], duration)
            metrics["max_time"] = max(metrics["max_time"], duration)

            if status_code not in metrics["status_codes"]:
                metrics["status_codes"][status_code] = 0
            metrics["status_codes"][status_code] += 1

            # Keep recent requests
            self.requests.append(
                {
                    "endpoint": endpoint,
                    "method": method,
                    "duration": duration,
                    "status_code": status_code,
                    "timestamp": datetime.utcnow(),
                }
            )

            # Keep only last 1000 requests
            if len(self.requests) > 1000:
                self.requests = self.requests[-1000:]

    def record_error(
        self, error: Exception, endpoint: str, user_id: Optional[int] = None
    ):
        """Record error metrics."""
        with self.lock:
            self.errors.append(
                {
                    "error": str(error),
                    "type": type(error).__name__,
                    "endpoint": endpoint,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow(),
                }
            )

            # Keep only last 500 errors
            if len(self.errors) > 500:
                self.errors = self.errors[-500:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        with self.lock:
            # Calculate overall stats
            total_requests = sum(m["count"] for m in self.metrics.values())
            avg_response_time = (
                sum(m["avg_time"] for m in self.metrics.values()) / len(self.metrics)
                if self.metrics
                else 0
            )

            # Recent errors (last hour)
            recent_errors = [
                e
                for e in self.errors
                if e["timestamp"] > datetime.utcnow() - timedelta(hours=1)
            ]

            return {
                "total_requests": total_requests,
                "avg_response_time": avg_response_time,
                "recent_errors": len(recent_errors),
                "error_rate": len(recent_errors) / max(total_requests, 1) * 100,
                "endpoints": dict(
                    sorted(
                        self.metrics.items(),
                        key=lambda x: x[1]["avg_time"],
                        reverse=True,
                    )[:10]
                ),
                "recent_requests": self.requests[-10:],
                "recent_errors_detail": recent_errors[-10:],
            }


# Global performance monitor
perf_monitor = PerformanceMonitor()


def monitor_performance(f):
    """Decorator to monitor endpoint performance."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        status_code = 200

        try:
            result = f(*args, **kwargs)
            if hasattr(result, "status_code"):
                status_code = result.status_code
            return result
        except Exception as e:
            status_code = 500
            perf_monitor.record_error(
                e, request.endpoint, getattr(g, "current_user_id", None)
            )
            raise
        finally:
            duration = time.time() - start_time
            perf_monitor.record_request(
                request.endpoint or "unknown", request.method, duration, status_code
            )

    return decorated_function


class StructuredLogger:
    """Structured logging with JSON format."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log(self, level: str, message: str, **kwargs):
        """Log structured message."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "message": message,
            "request_id": getattr(g, "request_id", None),
            "user_id": getattr(g, "current_user_id", None),
            "ip_address": request.remote_addr if request else None,
            "user_agent": request.headers.get("User-Agent") if request else None,
            **kwargs,
        }

        getattr(self.logger, level.lower())(json.dumps(log_data))

    def info(self, message: str, **kwargs):
        self.log("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.log("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log("error", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self.log("debug", message, **kwargs)


def setup_advanced_logging(app):
    """Setup advanced logging configuration."""

    # Create logs directory
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # JSON formatter
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            return json.dumps(log_data)

    # Application logs
    app_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=10485760, backupCount=10  # 10MB
    )
    app_handler.setFormatter(JSONFormatter())
    app_handler.setLevel(logging.INFO)

    # Error logs
    error_handler = RotatingFileHandler(
        "logs/errors.log", maxBytes=10485760, backupCount=5  # 10MB
    )
    error_handler.setFormatter(JSONFormatter())
    error_handler.setLevel(logging.ERROR)

    # Performance logs
    perf_handler = RotatingFileHandler(
        "logs/performance.log", maxBytes=10485760, backupCount=5  # 10MB
    )
    perf_handler.setFormatter(JSONFormatter())
    perf_handler.setLevel(logging.INFO)

    # Security logs
    security_handler = RotatingFileHandler(
        "logs/security.log", maxBytes=10485760, backupCount=10  # 10MB
    )
    security_handler.setFormatter(JSONFormatter())
    security_handler.setLevel(logging.WARNING)

    # Email alerts for critical errors
    if not app.debug and app.config.get("MAIL_SERVER"):
        mail_handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr=app.config["MAIL_DEFAULT_SENDER"],
            toaddrs=[app.config.get("ADMIN_EMAIL", "admin@example.com")],
            subject="Application Error",
            credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]),
            secure=() if app.config["MAIL_USE_TLS"] else None,
        )
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(JSONFormatter())
        app.logger.addHandler(mail_handler)

    # Add handlers to loggers
    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)

    # Create specialized loggers
    perf_logger = logging.getLogger("performance")
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)

    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)

    app.logger.setLevel(logging.INFO)


def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security-related events."""
    security_logger = StructuredLogger("security")
    security_logger.warning(f"Security event: {event_type}", **details)


def log_performance_metric(metric_name: str, value: float, **kwargs):
    """Log performance metrics."""
    perf_logger = StructuredLogger("performance")
    perf_logger.info(f"Performance metric: {metric_name}", value=value, **kwargs)
