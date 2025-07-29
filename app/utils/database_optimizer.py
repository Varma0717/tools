"""
Database optimization and monitoring utilities.
"""

import time
from functools import wraps
from typing import Dict, List, Any
from flask import current_app, g
from sqlalchemy import event, inspect
from sqlalchemy.engine import Engine
from app.core.extensions import db
import logging


class DatabaseMonitor:
    """Database performance monitoring."""

    def __init__(self):
        self.query_stats = {}
        self.slow_queries = []
        self.connection_count = 0

    def track_query(self, statement, parameters, duration):
        """Track query execution."""
        if statement not in self.query_stats:
            self.query_stats[statement] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "min_time": float("inf"),
                "max_time": 0,
            }

        stats = self.query_stats[statement]
        stats["count"] += 1
        stats["total_time"] += duration
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["min_time"] = min(stats["min_time"], duration)
        stats["max_time"] = max(stats["max_time"], duration)

        # Track slow queries
        if duration > 1.0:  # Queries slower than 1 second
            self.slow_queries.append(
                {
                    "statement": statement,
                    "parameters": parameters,
                    "duration": duration,
                    "timestamp": time.time(),
                }
            )

    def get_stats(self) -> Dict:
        """Get database statistics."""
        return {
            "total_queries": sum(stats["count"] for stats in self.query_stats.values()),
            "average_query_time": (
                sum(stats["avg_time"] for stats in self.query_stats.values())
                / len(self.query_stats)
                if self.query_stats
                else 0
            ),
            "slow_queries": len(self.slow_queries),
            "connection_count": self.connection_count,
            "top_queries": sorted(
                self.query_stats.items(), key=lambda x: x[1]["total_time"], reverse=True
            )[:10],
        }


# Global monitor instance
db_monitor = DatabaseMonitor()


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query start time."""
    context._query_start_time = time.time()


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query completion and performance."""
    total = time.time() - context._query_start_time
    db_monitor.track_query(statement, parameters, total)

    # Log slow queries
    if total > 1.0:
        current_app.logger.warning(
            f"Slow query detected: {total:.2f}s - {statement[:100]}..."
        )


def optimize_query(model_class):
    """Decorator to optimize common queries."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Add query optimization hints
            with db.session.no_autoflush:
                result = f(*args, **kwargs)
            return result

        return decorated_function

    return decorator


class DatabaseOptimizer:
    """Database optimization utilities."""

    @staticmethod
    def analyze_table_stats():
        """Analyze table statistics."""
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        stats = {}
        for table in tables:
            try:
                result = db.session.execute(
                    f"SELECT COUNT(*) as row_count FROM {table}"
                ).fetchone()
                stats[table] = {
                    "row_count": result[0] if result else 0,
                    "indexes": inspector.get_indexes(table),
                    "foreign_keys": inspector.get_foreign_keys(table),
                }
            except Exception as e:
                stats[table] = {"error": str(e)}

        return stats

    @staticmethod
    def suggest_indexes():
        """Suggest database indexes based on query patterns."""
        suggestions = []

        # Analyze slow queries for index suggestions
        for query_data in db_monitor.slow_queries:
            statement = query_data["statement"].lower()

            # Look for WHERE clauses without indexes
            if "where" in statement and "index" not in statement:
                suggestions.append(
                    {
                        "query": statement[:100] + "...",
                        "suggestion": "Consider adding an index on the WHERE clause columns",
                        "duration": query_data["duration"],
                    }
                )

        return suggestions

    @staticmethod
    def vacuum_analyze():
        """Perform database maintenance (PostgreSQL/MySQL specific)."""
        try:
            if "postgresql" in str(db.engine.url):
                db.session.execute("VACUUM ANALYZE;")
            elif "mysql" in str(db.engine.url):
                db.session.execute("OPTIMIZE TABLE posts, users, categories;")

            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Database maintenance failed: {e}")
            return False


def bulk_insert_optimized(
    model_class, data_list: List[Dict[str, Any]], batch_size: int = 1000
):
    """Optimized bulk insert operation."""
    try:
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i : i + batch_size]
            db.session.bulk_insert_mappings(model_class, batch)
            db.session.commit()

        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Bulk insert failed: {e}")
        return False


def connection_pool_status():
    """Get database connection pool status."""
    pool = db.engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid(),
    }
