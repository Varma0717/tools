"""
Rate limiting and security middleware.
"""

import time
from collections import defaultdict, deque
from functools import wraps
from typing import Dict, Tuple, Optional
from flask import request, jsonify, current_app, g
from werkzeug.exceptions import TooManyRequests
import hashlib


class RateLimiter:
    """Advanced rate limiter with sliding window."""

    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, float] = {}

    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Check if request is allowed."""
        now = time.time()

        # Check if IP is temporarily blocked
        if key in self.blocked_ips:
            if now < self.blocked_ips[key]:
                return False, 0
            else:
                del self.blocked_ips[key]

        # Clean old requests
        requests = self.requests[key]
        while requests and requests[0] <= now - window:
            requests.popleft()

        # Check rate limit
        if len(requests) >= limit:
            # Block IP for 5 minutes if exceeded
            self.blocked_ips[key] = now + 300
            return False, 0

        # Add current request
        requests.append(now)
        remaining = limit - len(requests)
        return True, remaining

    def reset_key(self, key: str):
        """Reset rate limit for a key."""
        if key in self.requests:
            del self.requests[key]
        if key in self.blocked_ips:
            del self.blocked_ips[key]


# Global rate limiter
rate_limiter = RateLimiter()


def rate_limit(per_minute: int = 60, per_hour: int = 1000):
    """Rate limiting decorator."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
            if "," in client_ip:
                client_ip = client_ip.split(",")[0].strip()

            user_id = getattr(g, "current_user_id", None)
            key = f"user:{user_id}" if user_id else f"ip:{client_ip}"

            # Check minute limit
            allowed, remaining = rate_limiter.is_allowed(
                f"{key}:minute", per_minute, 60
            )
            if not allowed:
                return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

            # Check hour limit
            allowed, _ = rate_limiter.is_allowed(f"{key}:hour", per_hour, 3600)
            if not allowed:
                return jsonify({"error": "Hourly rate limit exceeded."}), 429

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def security_headers(f):
    """Add security headers to response."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)

        # Add security headers
        if hasattr(response, "headers"):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
            )

        return response

    return decorated_function


def validate_input(schema: dict):
    """Input validation decorator."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                errors = []

                for field, rules in schema.items():
                    value = data.get(field)

                    # Required field check
                    if rules.get("required", False) and not value:
                        errors.append(f"{field} is required")
                        continue

                    if value is None:
                        continue

                    # Type check
                    expected_type = rules.get("type")
                    if expected_type and not isinstance(value, expected_type):
                        errors.append(
                            f"{field} must be of type {expected_type.__name__}"
                        )

                    # Length check
                    if "max_length" in rules and len(str(value)) > rules["max_length"]:
                        errors.append(
                            f"{field} exceeds maximum length of {rules['max_length']}"
                        )

                    # Pattern check
                    if "pattern" in rules:
                        import re

                        if not re.match(rules["pattern"], str(value)):
                            errors.append(f"{field} format is invalid")

                if errors:
                    return jsonify({"errors": errors}), 400

            return f(*args, **kwargs)

        return decorated_function

    return decorator
