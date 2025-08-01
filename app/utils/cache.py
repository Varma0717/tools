"""
Advanced caching layer for Flask application.
"""

import functools
import hashlib
import json
import pickle
import time
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Callable
from flask import current_app, request


# Simple in-memory cache implementation
class SimpleCache:
    """Simple in-memory cache with expiration."""

    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> Any:
        """Get value from cache."""
        if key in self._cache:
            value, expires = self._cache[key]
            if expires is None or time.time() < expires:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set value in cache."""
        expires = time.time() + timeout if timeout else None
        self._cache[key] = (value, expires)
        return True

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> bool:
        """Clear all cache."""
        self._cache.clear()
        return True


try:
    import redis

    REDIS_AVAILABLE = True

    class RedisSimpleCache:
        """Simple Redis-based cache."""

        def __init__(self, redis_client):
            self.redis = redis_client

        def get(self, key: str) -> Any:
            """Get value from Redis cache."""
            try:
                value = self.redis.get(key)
                if value:
                    return pickle.loads(value)
            except:
                pass
            return None

        def set(self, key: str, value: Any, timeout: int = 300) -> bool:
            """Set value in Redis cache."""
            try:
                serialized = pickle.dumps(value)
                return self.redis.setex(key, timeout, serialized)
            except:
                return False

        def delete(self, key: str) -> bool:
            """Delete value from Redis cache."""
            try:
                return bool(self.redis.delete(key))
            except:
                return False

        def clear(self) -> bool:
            """Clear all cache."""
            try:
                return self.redis.flushdb()
            except:
                return False

except ImportError:
    REDIS_AVAILABLE = False


class CacheManager:
    """Advanced caching manager with multiple backends."""

    def __init__(self, app=None):
        self.cache = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize cache with Flask app."""
        cache_type = app.config.get("CACHE_TYPE", "simple")

        if cache_type == "redis" and REDIS_AVAILABLE:
            redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
            try:
                redis_client = redis.from_url(redis_url)
                # Simple Redis-based cache implementation
                self.cache = RedisSimpleCache(redis_client)
            except:
                # Fallback to simple cache if Redis is not available
                self.cache = SimpleCache()
        else:
            self.cache = SimpleCache()

    def get(self, key: str) -> Any:
        """Get value from cache."""
        if not self.cache:
            return None
        return self.cache.get(key)

    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set value in cache."""
        if not self.cache:
            return False
        return self.cache.set(key, value, timeout)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.cache:
            return False
        return self.cache.delete(key)

    def clear(self) -> bool:
        """Clear all cache."""
        if not self.cache:
            return False
        return self.cache.clear()


# Global cache instance
cache = CacheManager()


def cached(timeout: int = 300, key_prefix: str = "view"):
    """Decorator for caching view functions."""

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = (
                f"{key_prefix}::{request.path}::{request.query_string.decode('utf-8')}"
            )
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return decorated_function

    return decorator


def cache_model(model_class, timeout: int = 600):
    """Cache model queries."""

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"model::{model_class.__name__}::{f.__name__}::{str(args)}::{str(kwargs)}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return decorated_function

    return decorator
