from flask import abort, request, jsonify
from flask_login import current_user
from functools import wraps
import time
from collections import defaultdict, deque

# Simple in-memory rate limiting storage
rate_limit_storage = defaultdict(lambda: deque())


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def rate_limit(max_requests=60, window=3600, per="ip"):
    """
    Simple rate limiting decorator

    Args:
        max_requests: Maximum number of requests allowed
        window: Time window in seconds
        per: Rate limit per 'ip' or 'user'
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get identifier
            if per == "ip":
                identifier = request.remote_addr or "unknown"
            elif per == "user" and current_user.is_authenticated:
                identifier = str(current_user.id)
            else:
                identifier = request.remote_addr or "unknown"

            # Clean old entries
            now = time.time()
            requests_list = rate_limit_storage[f"{f.__name__}:{identifier}"]

            # Remove requests outside the window
            while requests_list and requests_list[0] < now - window:
                requests_list.popleft()

            # Check if limit exceeded
            if len(requests_list) >= max_requests:
                return (
                    jsonify(
                        {
                            "error": "Rate limit exceeded",
                            "message": f"Maximum {max_requests} requests per {window//60} minutes",
                        }
                    ),
                    429,
                )

            # Add current request
            requests_list.append(now)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
