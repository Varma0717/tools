"""
Cache Performance Optimization Tool
Analyzes cache usage patterns and provides optimization recommendations
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import sqlite3
import os
import sys

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import current_app

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

    class MockCurrentApp:
        class logger:
            @staticmethod
            def error(msg):
                print(f"ERROR: {msg}")

            @staticmethod
            def warning(msg):
                print(f"WARNING: {msg}")

            @staticmethod
            def info(msg):
                print(f"INFO: {msg}")

    current_app = MockCurrentApp()

try:
    from utils.advanced_caching import get_smart_cache_manager
    from utils.caching import get_cache_manager

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("⚠️  Cache modules not available - running in standalone mode")


class CacheProfiler:
    """Profile cache operations for optimization insights"""

    def __init__(self, db_path: str = "cache_profile.db"):
        self.db_path = db_path
        self.init_database()
        self.lock = threading.Lock()

    def init_database(self):
        """Initialize SQLite database for profiling data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    cache_key TEXT NOT NULL,
                    duration REAL NOT NULL,
                    success INTEGER NOT NULL,
                    key_size INTEGER DEFAULT 0,
                    value_size INTEGER DEFAULT 0,
                    ttl INTEGER DEFAULT 0
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON cache_operations(timestamp)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cache_key 
                ON cache_operations(cache_key)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_operation 
                ON cache_operations(operation)
            """
            )

    def record_operation(
        self,
        operation: str,
        cache_key: str,
        duration: float,
        success: bool,
        key_size: int = 0,
        value_size: int = 0,
        ttl: int = 0,
    ):
        """Record a cache operation for analysis"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO cache_operations 
                        (timestamp, operation, cache_key, duration, success, key_size, value_size, ttl)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            datetime.now().isoformat(),
                            operation,
                            cache_key,
                            duration,
                            1 if success else 0,
                            key_size,
                            value_size,
                            ttl,
                        ),
                    )
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Error recording cache operation: {e}")

    def get_performance_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance analysis"""
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Overall statistics
            overall_stats = conn.execute(
                """
                SELECT 
                    operation,
                    COUNT(*) as count,
                    AVG(duration) as avg_duration,
                    MIN(duration) as min_duration,
                    MAX(duration) as max_duration,
                    SUM(success) as success_count,
                    AVG(value_size) as avg_value_size
                FROM cache_operations 
                WHERE timestamp > ?
                GROUP BY operation
            """,
                (cutoff_time,),
            ).fetchall()

            # Key performance analysis
            key_stats = conn.execute(
                """
                SELECT 
                    cache_key,
                    COUNT(*) as total_operations,
                    SUM(CASE WHEN operation = 'get' AND success = 1 THEN 1 ELSE 0 END) as hits,
                    SUM(CASE WHEN operation = 'get' AND success = 0 THEN 1 ELSE 0 END) as misses,
                    AVG(duration) as avg_duration,
                    MAX(value_size) as max_value_size
                FROM cache_operations 
                WHERE timestamp > ?
                GROUP BY cache_key
                ORDER BY total_operations DESC
                LIMIT 50
            """,
                (cutoff_time,),
            ).fetchall()

            # Slowest operations
            slow_operations = conn.execute(
                """
                SELECT cache_key, operation, duration, timestamp
                FROM cache_operations 
                WHERE timestamp > ?
                ORDER BY duration DESC
                LIMIT 20
            """,
                (cutoff_time,),
            ).fetchall()

            # Hourly patterns
            hourly_stats = conn.execute(
                """
                SELECT 
                    strftime('%H', timestamp) as hour,
                    COUNT(*) as operations,
                    AVG(duration) as avg_duration
                FROM cache_operations 
                WHERE timestamp > ?
                GROUP BY strftime('%H', timestamp)
                ORDER BY hour
            """,
                (cutoff_time,),
            ).fetchall()

        return {
            "analysis_period": f"Last {hours} hours",
            "overall_stats": [dict(row) for row in overall_stats],
            "key_performance": [
                {
                    **dict(row),
                    "hit_rate": (
                        (row["hits"] / (row["hits"] + row["misses"]) * 100)
                        if (row["hits"] + row["misses"]) > 0
                        else 0
                    ),
                }
                for row in key_stats
            ],
            "slowest_operations": [dict(row) for row in slow_operations],
            "hourly_patterns": [dict(row) for row in hourly_stats],
        }


class CacheOptimizer:
    """Analyze cache patterns and provide optimization recommendations"""

    def __init__(self, profiler: CacheProfiler = None):
        self.profiler = profiler or CacheProfiler()
        if CACHE_AVAILABLE:
            self.smart_cache = get_smart_cache_manager()
            self.cache_manager = get_cache_manager()
        else:
            self.smart_cache = None
            self.cache_manager = None

    def analyze_key_patterns(
        self, analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze cache key patterns for optimization opportunities"""
        recommendations = []

        key_performance = analysis_data.get("key_performance", [])

        for key_data in key_performance:
            key = key_data["cache_key"]
            hit_rate = key_data["hit_rate"]
            total_ops = key_data["total_operations"]
            avg_duration = key_data["avg_duration"]
            max_size = key_data["max_value_size"]

            # Low hit rate recommendation
            if hit_rate < 30 and total_ops > 10:
                recommendations.append(
                    {
                        "type": "low_hit_rate",
                        "key": key,
                        "hit_rate": hit_rate,
                        "recommendation": "Consider removing or adjusting TTL - low cache effectiveness",
                        "priority": "high",
                    }
                )

            # High latency recommendation
            if avg_duration > 0.1:  # 100ms
                recommendations.append(
                    {
                        "type": "high_latency",
                        "key": key,
                        "avg_duration": avg_duration,
                        "recommendation": "Investigate slow cache operations - possible network/serialization issues",
                        "priority": "medium",
                    }
                )

            # Large value recommendation
            if max_size > 1024 * 1024:  # 1MB
                recommendations.append(
                    {
                        "type": "large_value",
                        "key": key,
                        "max_size": max_size,
                        "recommendation": "Consider compressing large cached values or breaking into smaller chunks",
                        "priority": "medium",
                    }
                )

            # High frequency recommendation
            if total_ops > 1000 and hit_rate > 80:
                recommendations.append(
                    {
                        "type": "high_frequency",
                        "key": key,
                        "total_operations": total_ops,
                        "hit_rate": hit_rate,
                        "recommendation": "Consider longer TTL or cache warming for frequently accessed data",
                        "priority": "low",
                    }
                )

        return recommendations

    def analyze_temporal_patterns(
        self, analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze temporal access patterns"""
        recommendations = []

        hourly_patterns = analysis_data.get("hourly_patterns", [])

        if hourly_patterns:
            # Find peak hours
            max_ops = max(hour["operations"] for hour in hourly_patterns)
            peak_hours = [
                hour for hour in hourly_patterns if hour["operations"] > max_ops * 0.8
            ]

            if len(peak_hours) > 0:
                peak_hour_list = [hour["hour"] for hour in peak_hours]
                recommendations.append(
                    {
                        "type": "temporal_pattern",
                        "peak_hours": peak_hour_list,
                        "recommendation": f'Consider cache warming before peak hours: {", ".join(peak_hour_list)}',
                        "priority": "medium",
                    }
                )

            # Find low activity periods
            min_ops = min(hour["operations"] for hour in hourly_patterns)
            low_activity_hours = [
                hour for hour in hourly_patterns if hour["operations"] < min_ops * 1.5
            ]

            if len(low_activity_hours) > 2:
                low_hours = [hour["hour"] for hour in low_activity_hours]
                recommendations.append(
                    {
                        "type": "maintenance_window",
                        "low_activity_hours": low_hours,
                        "recommendation": f'Schedule cache maintenance during low activity: {", ".join(low_hours)}',
                        "priority": "low",
                    }
                )

        return recommendations

    def generate_optimization_plan(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive optimization plan"""
        # Get performance analysis
        analysis = self.profiler.get_performance_analysis(hours)

        # Generate recommendations
        key_recommendations = self.analyze_key_patterns(analysis)
        temporal_recommendations = self.analyze_temporal_patterns(analysis)

        # Combine recommendations
        all_recommendations = key_recommendations + temporal_recommendations

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        all_recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        # Generate summary statistics
        overall_stats = analysis.get("overall_stats", [])
        total_operations = sum(stat["count"] for stat in overall_stats)
        avg_response_time = (
            sum(stat["avg_duration"] * stat["count"] for stat in overall_stats)
            / total_operations
            if total_operations > 0
            else 0
        )

        get_operations = next(
            (stat for stat in overall_stats if stat["operation"] == "get"),
            {"count": 0, "success_count": 0},
        )
        overall_hit_rate = (
            (get_operations["success_count"] / get_operations["count"] * 100)
            if get_operations["count"] > 0
            else 0
        )

        return {
            "analysis_period": analysis["analysis_period"],
            "summary": {
                "total_operations": total_operations,
                "overall_hit_rate": overall_hit_rate,
                "average_response_time": avg_response_time,
                "total_recommendations": len(all_recommendations),
            },
            "recommendations": all_recommendations,
            "detailed_analysis": analysis,
        }

    def implement_auto_optimizations(
        self, optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Automatically implement safe optimizations"""
        implemented = []
        skipped = []

        for rec in optimization_plan["recommendations"]:
            if rec["type"] == "low_hit_rate" and rec["priority"] == "high":
                # Auto-remove keys with very low hit rates
                if rec["hit_rate"] < 10:
                    key = rec["key"]
                    if self.cache_manager.delete(key):
                        implemented.append(
                            {
                                "action": "deleted_low_performance_key",
                                "key": key,
                                "reason": f'Hit rate: {rec["hit_rate"]:.1f}%',
                            }
                        )
                    else:
                        skipped.append(
                            {
                                "action": "failed_to_delete_key",
                                "key": key,
                                "reason": "Delete operation failed",
                            }
                        )

            elif rec["type"] == "high_frequency" and rec["priority"] == "low":
                # Add cache warming for high-frequency, high-hit-rate keys
                key = rec["key"]
                if not any(
                    rule["key_pattern"] == key
                    for rule in self.smart_cache.cache_warming_rules
                ):
                    # This would require more context about how to fetch the data
                    skipped.append(
                        {
                            "action": "skip_cache_warming",
                            "key": key,
                            "reason": "No fetch function available for automatic warming",
                        }
                    )

            else:
                skipped.append(
                    {
                        "action": "manual_review_required",
                        "recommendation": rec,
                        "reason": "Requires manual intervention",
                    }
                )

        return {
            "implemented": implemented,
            "skipped": skipped,
            "timestamp": datetime.now().isoformat(),
        }


class CacheMonitor:
    """Real-time cache monitoring and alerting"""

    def __init__(self, profiler: CacheProfiler = None):
        self.profiler = profiler or CacheProfiler()
        self.alerts = []
        self.thresholds = {
            "max_response_time": 0.5,  # 500ms
            "min_hit_rate": 60.0,  # 60%
            "max_error_rate": 5.0,  # 5%
        }
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, interval: int = 60):
        """Start real-time monitoring"""
        if self.monitoring:
            return

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                try:
                    self.check_performance_alerts()
                    time.sleep(interval)
                except Exception as e:
                    if current_app:
                        current_app.logger.error(f"Cache monitoring error: {e}")
                    time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        if current_app:
            current_app.logger.info("Cache monitoring started")

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def check_performance_alerts(self):
        """Check for performance issues and generate alerts"""
        analysis = self.profiler.get_performance_analysis(hours=1)  # Last hour

        overall_stats = analysis.get("overall_stats", [])

        for stat in overall_stats:
            operation = stat["operation"]
            avg_duration = stat["avg_duration"]
            count = stat["count"]
            success_rate = (stat["success_count"] / count * 100) if count > 0 else 100

            # Check response time
            if avg_duration > self.thresholds["max_response_time"]:
                self.add_alert(
                    {
                        "type": "high_response_time",
                        "operation": operation,
                        "value": avg_duration,
                        "threshold": self.thresholds["max_response_time"],
                        "message": f'{operation} operations averaging {avg_duration:.3f}s (threshold: {self.thresholds["max_response_time"]}s)',
                    }
                )

            # Check success rate for get operations
            if operation == "get" and success_rate < self.thresholds["min_hit_rate"]:
                self.add_alert(
                    {
                        "type": "low_hit_rate",
                        "operation": operation,
                        "value": success_rate,
                        "threshold": self.thresholds["min_hit_rate"],
                        "message": f'Cache hit rate: {success_rate:.1f}% (threshold: {self.thresholds["min_hit_rate"]}%)',
                    }
                )

            # Check error rate
            error_rate = (
                ((count - stat["success_count"]) / count * 100) if count > 0 else 0
            )
            if error_rate > self.thresholds["max_error_rate"]:
                self.add_alert(
                    {
                        "type": "high_error_rate",
                        "operation": operation,
                        "value": error_rate,
                        "threshold": self.thresholds["max_error_rate"],
                        "message": f'{operation} error rate: {error_rate:.1f}% (threshold: {self.thresholds["max_error_rate"]}%)',
                    }
                )

    def add_alert(self, alert: Dict[str, Any]):
        """Add an alert"""
        alert["timestamp"] = datetime.now().isoformat()
        alert["id"] = len(self.alerts)

        self.alerts.append(alert)

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        if current_app:
            current_app.logger.warning(f"Cache Alert: {alert['message']}")

    def get_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [
            alert
            for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
        ]


# Global instances
cache_profiler = None
cache_optimizer = None
cache_monitor = None


def get_cache_profiler() -> CacheProfiler:
    """Get or create cache profiler"""
    global cache_profiler
    if cache_profiler is None:
        cache_profiler = CacheProfiler()
    return cache_profiler


def get_cache_optimizer() -> CacheOptimizer:
    """Get or create cache optimizer"""
    global cache_optimizer
    if cache_optimizer is None:
        cache_optimizer = CacheOptimizer()
    return cache_optimizer


def get_cache_monitor() -> CacheMonitor:
    """Get or create cache monitor"""
    global cache_monitor
    if cache_monitor is None:
        cache_monitor = CacheMonitor()
    return cache_monitor


# CLI functions for cache optimization
def run_cache_analysis(hours: int = 24) -> Dict[str, Any]:
    """Run comprehensive cache analysis"""
    if not CACHE_AVAILABLE:
        return {
            "error": "Cache modules not available",
            "analysis_period": f"Last {hours} hours",
            "summary": {
                "total_operations": 0,
                "overall_hit_rate": 0,
                "average_response_time": 0,
                "total_recommendations": 0,
            },
            "recommendations": [],
            "detailed_analysis": {
                "overall_stats": [],
                "key_performance": [],
                "slowest_operations": [],
                "hourly_patterns": [],
            },
        }

    optimizer = get_cache_optimizer()
    return optimizer.generate_optimization_plan(hours)


def optimize_cache_automatically() -> Dict[str, Any]:
    """Run automatic cache optimizations"""
    optimizer = get_cache_optimizer()
    plan = optimizer.generate_optimization_plan()
    return optimizer.implement_auto_optimizations(plan)


def start_cache_monitoring(interval: int = 60):
    """Start cache monitoring"""
    monitor = get_cache_monitor()
    monitor.start_monitoring(interval)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python cache_optimizer.py [analyze|optimize|monitor]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "analyze":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        result = run_cache_analysis(hours)
        print(json.dumps(result, indent=2))

    elif command == "optimize":
        result = optimize_cache_automatically()
        print(json.dumps(result, indent=2))

    elif command == "monitor":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"Starting cache monitoring (interval: {interval}s)")
        start_cache_monitoring(interval)

        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("Monitoring stopped")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
