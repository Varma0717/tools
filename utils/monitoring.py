"""
Advanced Monitoring and Observability System
Provides comprehensive application monitoring, metrics, and alerting
"""

import os
import time
import psutil
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
import json
from threading import Lock
from flask import request, g, current_app, jsonify
from utils.extensions import db


class MetricsCollector:
    """Collects and stores application metrics"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.lock = Lock()
        self.max_history = 1000

    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        with self.lock:
            key = self._build_key(name, tags)
            self.counters[key] += value

    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric"""
        with self.lock:
            key = self._build_key(name, tags)
            self.gauges[key] = value

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value"""
        with self.lock:
            key = self._build_key(name, tags)
            self.histograms[key].append({"value": value, "timestamp": time.time()})

            # Keep only recent values
            if len(self.histograms[key]) > self.max_history:
                self.histograms[key] = self.histograms[key][-self.max_history :]

    def record_timing(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record timing information"""
        self.record_histogram(f"{name}.duration", duration, tags)

    def _build_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """Build metric key with tags"""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        with self.lock:
            summary = {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {},
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Calculate histogram statistics
            for key, values in self.histograms.items():
                if values:
                    vals = [v["value"] for v in values]
                    summary["histograms"][key] = {
                        "count": len(vals),
                        "min": min(vals),
                        "max": max(vals),
                        "avg": sum(vals) / len(vals),
                        "p95": self._percentile(vals, 95),
                        "p99": self._percentile(vals, 99),
                    }

            return summary

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * percentile / 100
        f = int(k)
        c = k - f

        if f == len(sorted_values) - 1:
            return sorted_values[f]

        return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c


# Global metrics collector
metrics = MetricsCollector()


class PerformanceMonitor:
    """Monitors application performance"""

    def __init__(self):
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(
            lambda: {"count": 0, "total_time": 0, "errors": 0}
        )
        self.lock = Lock()

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration: float,
        user_id: Optional[int] = None,
    ):
        """Record request metrics"""
        with self.lock:
            # Record request timing
            self.request_times.append(
                {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                    "duration": duration,
                    "timestamp": time.time(),
                    "user_id": user_id,
                }
            )

            # Update endpoint statistics
            key = f"{method} {endpoint}"
            self.endpoint_stats[key]["count"] += 1
            self.endpoint_stats[key]["total_time"] += duration

            if status_code >= 400:
                self.endpoint_stats[key]["errors"] += 1
                self.error_counts[status_code] += 1

            # Record metrics
            metrics.increment_counter(
                "http_requests_total",
                1,
                {"method": method, "endpoint": endpoint, "status": str(status_code)},
            )

            metrics.record_timing(
                "http_request_duration",
                duration,
                {"method": method, "endpoint": endpoint},
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        with self.lock:
            now = time.time()
            recent_requests = [
                r
                for r in self.request_times
                if now - r["timestamp"] < 3600  # Last hour
            ]

            if not recent_requests:
                return {
                    "requests_per_hour": 0,
                    "avg_response_time": 0,
                    "error_rate": 0,
                    "slowest_endpoints": [],
                    "error_breakdown": {},
                }

            # Calculate metrics
            total_time = sum(r["duration"] for r in recent_requests)
            error_count = sum(1 for r in recent_requests if r["status_code"] >= 400)

            # Find slowest endpoints
            endpoint_times = defaultdict(list)
            for r in recent_requests:
                key = f"{r['method']} {r['endpoint']}"
                endpoint_times[key].append(r["duration"])

            slowest_endpoints = []
            for endpoint, times in endpoint_times.items():
                if times:
                    avg_time = sum(times) / len(times)
                    slowest_endpoints.append(
                        {
                            "endpoint": endpoint,
                            "avg_time": avg_time,
                            "count": len(times),
                        }
                    )

            slowest_endpoints.sort(key=lambda x: x["avg_time"], reverse=True)

            return {
                "requests_per_hour": len(recent_requests),
                "avg_response_time": total_time / len(recent_requests),
                "error_rate": error_count / len(recent_requests) * 100,
                "slowest_endpoints": slowest_endpoints[:10],
                "error_breakdown": dict(self.error_counts),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global performance monitor
performance_monitor = PerformanceMonitor()


class SystemMonitor:
    """Monitors system resources"""

    def __init__(self):
        self.process = psutil.Process()

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            process_memory = self.process.memory_info()

            # Disk metrics
            disk = psutil.disk_usage("/")

            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                }
            except:
                network_stats = {}

            # Database connections (if using SQLAlchemy)
            db_connections = 0
            try:
                if hasattr(db.engine, "pool"):
                    pool = db.engine.pool
                    db_connections = pool.checkedout()
            except:
                pass

            metrics_data = {
                "cpu": {"percent": cpu_percent, "count": cpu_count},
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "process_rss": process_memory.rss,
                    "process_vms": process_memory.vms,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                },
                "network": network_stats,
                "database": {"connections": db_connections},
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Record as metrics
            metrics.set_gauge("system.cpu.percent", cpu_percent)
            metrics.set_gauge("system.memory.percent", memory.percent)
            metrics.set_gauge("system.disk.percent", disk.percent)
            metrics.set_gauge("system.memory.process.rss", process_memory.rss)

            return metrics_data

        except Exception as e:
            current_app.logger.error(f"System metrics collection failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


# Global system monitor
system_monitor = SystemMonitor()


class AlertManager:
    """Manages alerts and notifications"""

    def __init__(self):
        self.alert_rules = []
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.lock = Lock()

    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add an alert rule"""
        with self.lock:
            self.alert_rules.append(rule)

    def check_alerts(self):
        """Check all alert rules"""
        with self.lock:
            current_metrics = metrics.get_metrics_summary()
            system_metrics = system_monitor.get_system_metrics()
            perf_metrics = performance_monitor.get_performance_summary()

            all_metrics = {
                "app": current_metrics,
                "system": system_metrics,
                "performance": perf_metrics,
            }

            for rule in self.alert_rules:
                try:
                    self._evaluate_rule(rule, all_metrics)
                except Exception as e:
                    current_app.logger.error(f"Alert rule evaluation failed: {e}")

    def _evaluate_rule(self, rule: Dict[str, Any], metrics_data: Dict[str, Any]):
        """Evaluate a single alert rule"""
        rule_id = rule["id"]
        condition = rule["condition"]
        threshold = rule["threshold"]
        message = rule["message"]
        severity = rule.get("severity", "warning")

        # Extract metric value based on condition path
        try:
            value = self._get_metric_value(condition, metrics_data)

            # Check threshold
            operator = rule.get("operator", "gt")
            is_triggered = self._check_threshold(value, operator, threshold)

            if is_triggered:
                if rule_id not in self.active_alerts:
                    # New alert
                    alert = {
                        "id": rule_id,
                        "message": message,
                        "severity": severity,
                        "value": value,
                        "threshold": threshold,
                        "triggered_at": datetime.utcnow().isoformat(),
                        "count": 1,
                    }

                    self.active_alerts[rule_id] = alert
                    self.alert_history.append(alert.copy())

                    # Send notification
                    self._send_alert_notification(alert)
                else:
                    # Update existing alert
                    self.active_alerts[rule_id]["count"] += 1
                    self.active_alerts[rule_id]["value"] = value

            else:
                # Alert resolved
                if rule_id in self.active_alerts:
                    resolved_alert = self.active_alerts.pop(rule_id)
                    resolved_alert["resolved_at"] = datetime.utcnow().isoformat()
                    self.alert_history.append(resolved_alert)

        except Exception as e:
            current_app.logger.error(f"Alert rule evaluation error: {e}")

    def _get_metric_value(self, path: str, data: Dict[str, Any]) -> float:
        """Extract metric value from nested data"""
        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise ValueError(f"Metric path not found: {path}")

        return float(value)

    def _check_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """Check if value meets threshold condition"""
        if operator == "gt":
            return value > threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "gte":
            return value >= threshold
        elif operator == "lte":
            return value <= threshold
        elif operator == "eq":
            return value == threshold
        else:
            return False

    def _send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification"""
        try:
            # Log alert
            current_app.logger.warning(
                f"ALERT [{alert['severity'].upper()}]: {alert['message']} "
                f"(Value: {alert['value']}, Threshold: {alert['threshold']})"
            )

            # Send email notification (if configured)
            if current_app.config.get("ALERT_EMAIL_ENABLED", False):
                # Import here to avoid circular imports
                from utils.tasks import send_email_async

                admin_email = current_app.config.get("ADMIN_EMAIL")
                if admin_email:
                    send_email_async.delay(
                        to_email=admin_email,
                        subject=f"Alert: {alert['message']}",
                        html_content=f"""
                        <h3>System Alert</h3>
                        <p><strong>Message:</strong> {alert['message']}</p>
                        <p><strong>Severity:</strong> {alert['severity']}</p>
                        <p><strong>Value:</strong> {alert['value']}</p>
                        <p><strong>Threshold:</strong> {alert['threshold']}</p>
                        <p><strong>Time:</strong> {alert['triggered_at']}</p>
                        """,
                    )

        except Exception as e:
            current_app.logger.error(f"Alert notification failed: {e}")

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        with self.lock:
            return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        with self.lock:
            return list(self.alert_history)[-limit:]


# Global alert manager
alert_manager = AlertManager()


# Initialize default alert rules
def setup_default_alerts():
    """Setup default alert rules"""
    default_rules = [
        {
            "id": "high_cpu",
            "condition": "system.cpu.percent",
            "operator": "gt",
            "threshold": 80.0,
            "message": "High CPU usage detected",
            "severity": "warning",
        },
        {
            "id": "high_memory",
            "condition": "system.memory.percent",
            "operator": "gt",
            "threshold": 85.0,
            "message": "High memory usage detected",
            "severity": "warning",
        },
        {
            "id": "high_error_rate",
            "condition": "performance.error_rate",
            "operator": "gt",
            "threshold": 5.0,
            "message": "High error rate detected",
            "severity": "critical",
        },
        {
            "id": "slow_response_time",
            "condition": "performance.avg_response_time",
            "operator": "gt",
            "threshold": 2.0,
            "message": "Slow response time detected",
            "severity": "warning",
        },
    ]

    for rule in default_rules:
        alert_manager.add_alert_rule(rule)


# Monitoring decorators


def monitor_performance(func: Callable = None, *, name: str = None):
    """Decorator to monitor function performance"""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = name or f"{f.__module__}.{f.__name__}"

            try:
                result = f(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                metrics.increment_counter(
                    f"function.errors", 1, {"function": func_name}
                )
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_timing(
                    f"function.duration",
                    duration,
                    {"function": func_name, "status": status},
                )
                metrics.increment_counter(
                    f"function.calls", 1, {"function": func_name, "status": status}
                )

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def monitor_requests():
    """Flask request monitoring middleware"""

    def before_request():
        g.start_time = time.time()

    def after_request(response):
        if hasattr(g, "start_time"):
            duration = time.time() - g.start_time

            # Get user ID if available
            user_id = None
            if (
                hasattr(g, "current_user")
                and g.current_user
                and hasattr(g.current_user, "id")
            ):
                user_id = g.current_user.id

            # Record request
            performance_monitor.record_request(
                endpoint=request.endpoint or "unknown",
                method=request.method,
                status_code=response.status_code,
                duration=duration,
                user_id=user_id,
            )

            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

        return response

    return before_request, after_request


# Health check endpoints


def create_health_endpoints(app):
    """Create health check endpoints"""

    @app.route("/health")
    def health_check():
        """Basic health check"""
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": app.config.get("APP_VERSION", "1.0.0"),
            }
        )

    @app.route("/health/detailed")
    def detailed_health_check():
        """Detailed health check with metrics"""
        try:
            # Test database connection
            db_healthy = True
            try:
                db.session.execute("SELECT 1")
                db.session.commit()
            except Exception as e:
                db_healthy = False
                db_error = str(e)

            # Test cache connection
            cache_healthy = True
            try:
                from utils.caching import cache_manager

                cache_health = (
                    cache_manager.redis_client.ping()
                    if cache_manager.redis_client
                    else False
                )
                cache_healthy = bool(cache_health)
            except Exception as e:
                cache_healthy = False
                cache_error = str(e)

            # Get system metrics
            system_metrics = system_monitor.get_system_metrics()

            health_data = {
                "status": "healthy" if db_healthy and cache_healthy else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "database": {
                        "status": "healthy" if db_healthy else "unhealthy",
                        "error": db_error if not db_healthy else None,
                    },
                    "cache": {
                        "status": "healthy" if cache_healthy else "unhealthy",
                        "error": cache_error if not cache_healthy else None,
                    },
                },
                "system": system_metrics,
                "performance": performance_monitor.get_performance_summary(),
            }

            status_code = 200 if db_healthy and cache_healthy else 503
            return jsonify(health_data), status_code

        except Exception as e:
            return (
                jsonify(
                    {
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                503,
            )

    @app.route("/metrics")
    def metrics_endpoint():
        """Prometheus-style metrics endpoint"""
        try:
            metrics_data = metrics.get_metrics_summary()

            # Convert to Prometheus format (simplified)
            output = []

            # Counters
            for name, value in metrics_data["counters"].items():
                output.append(f"{name} {value}")

            # Gauges
            for name, value in metrics_data["gauges"].items():
                output.append(f"{name} {value}")

            return "\n".join(output), 200, {"Content-Type": "text/plain"}

        except Exception as e:
            return f"# Error: {e}", 500, {"Content-Type": "text/plain"}

    @app.route("/alerts")
    def alerts_endpoint():
        """Get active alerts"""
        try:
            # Check alerts before returning
            alert_manager.check_alerts()

            return jsonify(
                {
                    "active_alerts": alert_manager.get_active_alerts(),
                    "alert_history": alert_manager.get_alert_history(50),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            return (
                jsonify({"error": str(e), "timestamp": datetime.utcnow().isoformat()}),
                500,
            )


# Initialize monitoring system
def init_monitoring(app):
    """Initialize monitoring system"""
    # Setup default alerts
    setup_default_alerts()

    # Register request monitoring
    before_request, after_request = monitor_requests()
    app.before_request(before_request)
    app.after_request(after_request)

    # Create health endpoints
    create_health_endpoints(app)

    # Start background alert checking (if using scheduler)
    # This would typically be done with a background task or cron job

    app.logger.info("Monitoring system initialized")


# Export main components
__all__ = [
    "metrics",
    "performance_monitor",
    "system_monitor",
    "alert_manager",
    "monitor_performance",
    "init_monitoring",
]
