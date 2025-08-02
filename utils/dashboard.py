"""
Performance Dashboard for Super SEO Toolkit
Provides real-time performance metrics and system health monitoring
"""

from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, timedelta
import json
from utils.monitoring import performance_monitor, system_monitor
from utils.caching import get_cache_manager
from utils.database_manager import get_database_health
from utils.decorators import admin_required, rate_limit

# Import enhanced cache components
try:
    from utils.advanced_caching import get_smart_cache_manager, smart_cache_health_check
    from utils.cache_optimizer import (
        get_cache_optimizer,
        get_cache_monitor,
        run_cache_analysis,
    )

    ADVANCED_CACHE_AVAILABLE = True
except ImportError:
    ADVANCED_CACHE_AVAILABLE = False


# Create blueprint for dashboard
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/admin/dashboard")


@dashboard_bp.route("/")
@admin_required
def dashboard_home():
    """Main dashboard page"""
    return render_template("admin/dashboard/index.html")


@dashboard_bp.route("/api/metrics")
@admin_required
@rate_limit(lambda: f"dashboard_metrics_{request.remote_addr}", limit=60, window=60)
def get_metrics():
    """Get current performance metrics"""
    try:
        # Get performance metrics
        metrics = performance_monitor.get_current_metrics()

        # Get system metrics
        system_metrics = system_monitor.get_system_metrics()

        # Get cache health
        cache_manager = get_cache_manager()
        from utils.caching import cache_health_check

        cache_health = cache_health_check()

        # Get advanced cache analytics if available
        advanced_cache_data = {}
        if ADVANCED_CACHE_AVAILABLE:
            try:
                smart_cache = get_smart_cache_manager()
                advanced_cache_data = {
                    "analytics": smart_cache.get_analytics(),
                    "health": smart_cache_health_check(),
                }
            except Exception as e:
                advanced_cache_data = {"error": str(e)}

        # Get database health
        db_health = get_database_health()

        response_data = {
            "timestamp": datetime.now().isoformat(),
            "performance": metrics,
            "system": system_metrics,
            "cache": cache_health,
            "database": db_health,
            "advanced_cache": advanced_cache_data if ADVANCED_CACHE_AVAILABLE else None,
            "status": (
                "healthy"
                if all(
                    [
                        metrics.get("status") == "healthy",
                        system_metrics.get("status") == "healthy",
                        cache_health.get("status") == "healthy",
                        db_health.get("status") == "healthy",
                    ]
                )
                else "warning"
            ),
        }

        return jsonify(response_data)

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@dashboard_bp.route("/api/metrics/history")
@admin_required
@rate_limit(lambda: f"dashboard_history_{request.remote_addr}", limit=30, window=60)
def get_metrics_history():
    """Get historical performance metrics"""
    try:
        # Get time range from query parameters
        hours = int(request.args.get("hours", 1))
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        # Get historical data
        history = performance_monitor.get_metrics_history(start_time, end_time)

        return jsonify(
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "data": history,
                "status": "success",
            }
        )

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@dashboard_bp.route("/api/alerts")
@admin_required
def get_active_alerts():
    """Get active system alerts"""
    try:
        from utils.monitoring import alert_manager

        alerts = alert_manager.get_active_alerts()

        return jsonify(
            {
                "alerts": alerts,
                "count": len(alerts),
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e), "alerts": [], "count": 0}), 500


@dashboard_bp.route("/api/cache/stats")
@admin_required
def get_cache_stats():
    """Get detailed cache statistics"""
    try:
        cache_manager = get_cache_manager()

        # Get cache statistics if Redis is available
        if cache_manager.redis_client:
            info = cache_manager.redis_client.info()

            stats = {
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "used_memory_peak_human": info.get("used_memory_peak_human"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "expired_keys": info.get("expired_keys", 0),
                "evicted_keys": info.get("evicted_keys", 0),
            }

            # Calculate hit rate
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            total_requests = hits + misses
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0

            stats["hit_rate"] = round(hit_rate, 2)
            stats["total_requests"] = total_requests

        else:
            stats = {"status": "fallback", "message": "Using in-memory cache fallback"}

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@dashboard_bp.route("/api/database/stats")
@admin_required
def get_database_stats():
    """Get detailed database statistics"""
    try:
        from utils.extensions import db
        from sqlalchemy import text

        stats = {}

        with db.session.begin():
            # Get table sizes and row counts
            tables_info = []

            # List of tables to check
            table_names = [
                "users",
                "posts",
                "contact_message",
                "subscribers",
                "page_views",
                "faq",
                "testimonials",
                "categories",
            ]

            for table in table_names:
                try:
                    # Get row count
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row_count = result.fetchone()[0]

                    tables_info.append({"table": table, "rows": row_count})

                except Exception:
                    # Table might not exist
                    continue

            stats["tables"] = tables_info
            stats["total_tables"] = len(tables_info)
            stats["total_rows"] = sum(table["rows"] for table in tables_info)

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@dashboard_bp.route("/api/system/health")
@admin_required
def get_system_health():
    """Get comprehensive system health check"""
    try:
        health_checks = {}

        # Check cache system
        from utils.caching import cache_health_check

        health_checks["cache"] = cache_health_check()

        # Check database
        health_checks["database"] = get_database_health()

        # Check system resources
        system_health = system_monitor.get_system_metrics()
        health_checks["system"] = {
            "status": (
                "healthy" if system_health.get("cpu_percent", 0) < 80 else "warning"
            ),
            "cpu_usage": system_health.get("cpu_percent"),
            "memory_usage": system_health.get("memory_percent"),
            "disk_usage": system_health.get("disk_percent"),
        }

        # Check background tasks
        try:
            from utils.tasks import get_task_stats

            health_checks["background_tasks"] = get_task_stats()
        except Exception:
            health_checks["background_tasks"] = {"status": "unavailable"}

        # Overall health status
        all_healthy = all(
            check.get("status") in ["healthy", "unavailable"]
            for check in health_checks.values()
        )

        return jsonify(
            {
                "overall_status": "healthy" if all_healthy else "warning",
                "checks": health_checks,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "overall_status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@dashboard_bp.route("/api/clear-cache", methods=["POST"])
@admin_required
def clear_cache():
    """Clear application cache"""
    try:
        cache_manager = get_cache_manager()

        # Get cache pattern to clear
        pattern = request.json.get("pattern", "*") if request.is_json else "*"

        # Clear cache
        cleared_count = cache_manager.flush_pattern(pattern)

        return jsonify(
            {
                "status": "success",
                "message": f"Cleared {cleared_count} cache entries",
                "pattern": pattern,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# Template filters for the dashboard
@dashboard_bp.app_template_filter("format_bytes")
def format_bytes(bytes_value):
    """Format bytes to human readable format"""
    try:
        bytes_value = float(bytes_value)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    except (ValueError, TypeError):
        return str(bytes_value)


@dashboard_bp.app_template_filter("format_duration")
def format_duration(seconds):
    """Format seconds to human readable duration"""
    try:
        seconds = float(seconds)
        if seconds < 1:
            return f"{seconds*1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    except (ValueError, TypeError):
        return str(seconds)


def register_dashboard(app):
    """Register dashboard blueprint with the app"""
    app.register_blueprint(dashboard_bp)

    # Add dashboard navigation to admin menu
    if not hasattr(app, "admin_menu_items"):
        app.admin_menu_items = []

    app.admin_menu_items.append(
        {
            "name": "Performance Dashboard",
            "url": "dashboard.dashboard_home",
            "icon": "fas fa-tachometer-alt",
            "order": 1,
        }
    )


# New cache analytics endpoints
@dashboard_bp.route("/api/cache/analytics")
@admin_required
@rate_limit(lambda: f"cache_analytics_{request.remote_addr}", limit=30, window=60)
def get_cache_analytics():
    """Get comprehensive cache analytics"""
    if not ADVANCED_CACHE_AVAILABLE:
        return jsonify({"error": "Advanced cache analytics not available"}), 404

    try:
        hours = int(request.args.get("hours", 24))
        optimizer = get_cache_optimizer()
        analysis = optimizer.generate_optimization_plan(hours)

        return jsonify(
            {
                "status": "success",
                "data": analysis,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@dashboard_bp.route("/api/cache/optimize", methods=["POST"])
@admin_required
@rate_limit(lambda: f"cache_optimize_{request.remote_addr}", limit=5, window=300)
def optimize_cache():
    """Run automatic cache optimizations"""
    if not ADVANCED_CACHE_AVAILABLE:
        return jsonify({"error": "Advanced cache optimization not available"}), 404

    try:
        optimizer = get_cache_optimizer()
        plan = optimizer.generate_optimization_plan()
        result = optimizer.implement_auto_optimizations(plan)

        return jsonify(
            {
                "status": "success",
                "data": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@dashboard_bp.route("/api/cache/alerts")
@admin_required
@rate_limit(lambda: f"cache_alerts_{request.remote_addr}", limit=60, window=60)
def get_cache_alerts():
    """Get cache performance alerts"""
    if not ADVANCED_CACHE_AVAILABLE:
        return jsonify({"error": "Cache monitoring not available"}), 404

    try:
        hours = int(request.args.get("hours", 24))
        monitor = get_cache_monitor()
        alerts = monitor.get_alerts(hours)

        return jsonify(
            {
                "status": "success",
                "data": alerts,
                "count": len(alerts),
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@dashboard_bp.route("/cache-analytics")
@admin_required
def cache_analytics_page():
    """Cache analytics page"""
    if not ADVANCED_CACHE_AVAILABLE:
        return (
            render_template(
                "errors/404.html", message="Advanced cache analytics not available"
            ),
            404,
        )

    return render_template("admin/dashboard/cache_analytics.html")
