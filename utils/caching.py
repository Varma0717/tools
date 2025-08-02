"""
Advanced Caching System for Super SEO Toolkit
Implements multi-layer caching with Redis backend
"""

import json
import pickle
import hashlib
from functools import wraps
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Dict, List
import redis
from flask import current_app, request, g
from utils.extensions import db


class CacheManager:
    """Advanced caching system with Redis backend"""

    def __init__(self, redis_client=None):
        self.redis_client = redis_client or self._get_redis_client()
        self.default_ttl = 3600  # 1 hour
        self.cache_prefix = "seo_toolkit:"

    def _get_redis_client(self):
        """Initialize Redis client with fallback"""
        try:
            from flask import has_app_context, current_app

            if has_app_context():
                host = current_app.config.get("REDIS_HOST", "localhost")
                port = current_app.config.get("REDIS_PORT", 6379)
                db = current_app.config.get("REDIS_DB", 0)
                password = current_app.config.get("REDIS_PASSWORD", None)
            else:
                # Fallback defaults when no app context
                host = "localhost"
                port = 6379
                db = 0
                password = None

            client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            client.ping()
            return client
        except (redis.ConnectionError, ImportError):
            # Fallback for when Redis is not installed or not available
            return None

    def _generate_key(self, key: str, prefix: str = None) -> str:
        """Generate cache key with prefix"""
        prefix = prefix or self.cache_prefix
        return f"{prefix}{key}"

    def get(self, key: str, default=None) -> Any:
        """Get value from cache"""
        try:
            if not self.redis_client:
                return default

            cache_key = self._generate_key(key)
            value = self.redis_client.get(cache_key)

            if value is None:
                return default

            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(value.encode("latin1"))
                except (pickle.PickleError, AttributeError):
                    return value

        except Exception as e:
            current_app.logger.error(f"Cache get error: {e}")
            return default

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            if not self.redis_client:
                return False

            cache_key = self._generate_key(key)
            ttl = ttl or self.default_ttl

            # Serialize value
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, default=str)
            elif isinstance(value, (int, float, str, bool)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = pickle.dumps(value).decode("latin1")

            return self.redis_client.setex(cache_key, ttl, serialized_value)

        except Exception as e:
            current_app.logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if not self.redis_client:
                return False

            cache_key = self._generate_key(key)
            return bool(self.redis_client.delete(cache_key))

        except Exception as e:
            current_app.logger.error(f"Cache delete error: {e}")
            return False

    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            if not self.redis_client:
                return 0

            pattern_key = self._generate_key(pattern)
            keys = self.redis_client.keys(pattern_key)

            if keys:
                return self.redis_client.delete(*keys)
            return 0

        except Exception as e:
            current_app.logger.error(f"Cache flush pattern error: {e}")
            return 0

    def increment(self, key: str, amount: int = 1, ttl: int = None) -> int:
        """Increment counter in cache"""
        try:
            if not self.redis_client:
                return amount

            cache_key = self._generate_key(key)

            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            pipe.incr(cache_key, amount)

            if ttl:
                pipe.expire(cache_key, ttl)

            results = pipe.execute()
            return results[0]

        except Exception as e:
            current_app.logger.error(f"Cache increment error: {e}")
            return amount


# Global cache manager instance (initialized lazily)
cache_manager = None


def get_cache_manager():
    """Get or create the global cache manager instance"""
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager()
    return cache_manager


def cached(ttl: int = 3600, key_func=None, vary_on_user=False):
    """
    Decorator for caching function results

    Args:
        ttl: Time to live in seconds
        key_func: Function to generate cache key
        vary_on_user: Include user ID in cache key
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                func_name = f"{func.__module__}.{func.__name__}"
                args_str = "_".join(str(arg) for arg in args)
                kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"func:{func_name}:{args_str}:{kwargs_str}"

            # Add user variation if requested
            if vary_on_user and hasattr(g, "current_user") and g.current_user:
                cache_key = f"user:{g.current_user.id}:{cache_key}"

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def cache_database_query(query_key: str, ttl: int = 1800):
    """
    Decorator for caching database queries

    Args:
        query_key: Unique identifier for the query
        ttl: Time to live in seconds (default 30 minutes)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key with query parameters
            params_hash = hashlib.md5(
                json.dumps(kwargs, sort_keys=True, default=str).encode()
            ).hexdigest()[:8]

            cache_key = f"db_query:{query_key}:{params_hash}"

            # Check cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute query and cache result
            result = func(*args, **kwargs)

            # Only cache if result is not None
            if result is not None:
                cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


class RateLimiter:
    """Redis-based rate limiting"""

    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager or get_cache_manager()

    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, dict]:
        """
        Check if action is allowed under rate limit

        Args:
            key: Unique identifier (IP, user_id, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds

        Returns:
            (is_allowed, info_dict)
        """
        try:
            current_time = int(datetime.now().timestamp())
            window_start = current_time - window

            rate_key = f"rate_limit:{key}:{window_start // window}"

            # Get current count
            current_count = self.cache_manager.get(rate_key, 0)

            if isinstance(current_count, str):
                current_count = int(current_count)

            # Check if limit exceeded
            if current_count >= limit:
                return False, {
                    "allowed": False,
                    "limit": limit,
                    "remaining": 0,
                    "reset_time": (window_start // window + 1) * window,
                    "retry_after": window - (current_time % window),
                }

            # Increment counter
            new_count = self.cache_manager.increment(rate_key, 1, window)

            return True, {
                "allowed": True,
                "limit": limit,
                "remaining": limit - new_count,
                "reset_time": (window_start // window + 1) * window,
                "retry_after": 0,
            }

        except Exception as e:
            current_app.logger.error(f"Rate limiting error: {e}")
            # Allow request if rate limiting fails
            return True, {
                "allowed": True,
                "limit": limit,
                "remaining": limit - 1,
                "reset_time": current_time + window,
                "retry_after": 0,
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(key_func, limit: int = 100, window: int = 3600, per_user: bool = False):
    """
    Decorator for rate limiting endpoints

    Args:
        key_func: Function to generate rate limit key
        limit: Maximum requests allowed
        window: Time window in seconds
        per_user: Apply limit per user instead of globally
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import jsonify, request, g

            # Generate rate limit key
            if per_user and hasattr(g, "current_user") and g.current_user:
                limit_key = f"user:{g.current_user.id}:{key_func()}"
            else:
                limit_key = key_func()

            # Check rate limit
            allowed, info = rate_limiter.is_allowed(limit_key, limit, window)

            if not allowed:
                return (
                    jsonify(
                        {
                            "error": "Rate limit exceeded",
                            "limit": info["limit"],
                            "remaining": info["remaining"],
                            "reset_time": info["reset_time"],
                            "retry_after": info["retry_after"],
                        }
                    ),
                    429,
                )

            # Add rate limit headers to response
            response = func(*args, **kwargs)

            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Limit"] = str(info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(info["reset_time"])

            return response

        return wrapper

    return decorator


# Utility functions for common caching patterns


def cache_user_data(user_id: int, data: dict, ttl: int = 1800):
    """Cache user-specific data"""
    cache_key = f"user_data:{user_id}"
    return cache_manager.set(cache_key, data, ttl)


def get_cached_user_data(user_id: int) -> Optional[dict]:
    """Get cached user data"""
    cache_key = f"user_data:{user_id}"
    return cache_manager.get(cache_key)


def invalidate_user_cache(user_id: int):
    """Invalidate all cached data for a user"""
    pattern = f"user:{user_id}:*"
    return cache_manager.flush_pattern(pattern)


def cache_api_response(endpoint: str, params: dict, response: dict, ttl: int = 600):
    """Cache API response"""
    params_hash = hashlib.md5(
        json.dumps(params, sort_keys=True, default=str).encode()
    ).hexdigest()[:8]

    cache_key = f"api_response:{endpoint}:{params_hash}"
    return cache_manager.set(cache_key, response, ttl)


def get_cached_api_response(endpoint: str, params: dict) -> Optional[dict]:
    """Get cached API response"""
    params_hash = hashlib.md5(
        json.dumps(params, sort_keys=True, default=str).encode()
    ).hexdigest()[:8]

    cache_key = f"api_response:{endpoint}:{params_hash}"
    return cache_manager.get(cache_key)


# Health check for cache system
def cache_health_check() -> dict:
    """Check cache system health"""
    try:
        test_key = "health_check"
        test_value = f"test_{datetime.now().timestamp()}"

        # Test set
        set_result = cache_manager.set(test_key, test_value, 60)

        # Test get
        get_result = cache_manager.get(test_key)

        # Test delete
        delete_result = cache_manager.delete(test_key)

        return {
            "status": "healthy",
            "redis_available": cache_manager.redis_client is not None,
            "set_success": set_result,
            "get_success": get_result == test_value,
            "delete_success": delete_result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "redis_available": False,
            "timestamp": datetime.now().isoformat(),
        }
