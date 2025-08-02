from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import secrets
import hashlib
from utils.extensions import db
from models.subscription import APIUsage, UsageTracking

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


class APIKey(db.Model):
    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    key_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    api_secret = db.Column(db.String(128))

    # Permissions
    permissions = db.Column(db.JSON, default=list)  # List of allowed endpoints
    daily_limit = db.Column(db.Integer, default=1000)
    monthly_limit = db.Column(db.Integer, default=10000)

    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def generate_key(self):
        """Generate a new API key"""
        self.api_key = secrets.token_urlsafe(32)
        self.api_secret = hashlib.sha256(
            (self.api_key + str(datetime.utcnow())).encode()
        ).hexdigest()

    def check_rate_limit(self):
        """Check if API key is within rate limits"""
        today = datetime.utcnow().date()

        # Check daily limit
        daily_usage = APIUsage.query.filter_by(
            api_key_id=self.api_key, usage_date=today
        ).first()

        if daily_usage and daily_usage.usage_count >= self.daily_limit:
            return False, "Daily limit exceeded"

        return True, "OK"

    def record_usage(self, endpoint, response_time=None, status_code=200):
        """Record API usage"""
        today = datetime.utcnow().date()

        usage = APIUsage.query.filter_by(
            api_key_id=self.api_key, endpoint=endpoint, usage_date=today
        ).first()

        if usage:
            usage.usage_count += 1
        else:
            usage = APIUsage(
                user_id=self.user_id,
                api_key_id=self.api_key,
                endpoint=endpoint,
                usage_date=today,
                response_time_ms=response_time,
                status_code=status_code,
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
            )
            db.session.add(usage)

        self.last_used = datetime.utcnow()
        db.session.commit()


def require_api_key(f):
    """Decorator to require API key authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")

        if not api_key:
            return (
                jsonify(
                    {
                        "error": "API key required",
                        "message": "Include X-API-Key header or api_key parameter",
                    }
                ),
                401,
            )

        # Validate API key
        key_obj = APIKey.query.filter_by(api_key=api_key, is_active=True).first()

        if not key_obj:
            return (
                jsonify(
                    {
                        "error": "Invalid API key",
                        "message": "API key not found or inactive",
                    }
                ),
                401,
            )

        # Check expiration
        if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
            return (
                jsonify(
                    {"error": "API key expired", "message": "Please renew your API key"}
                ),
                401,
            )

        # Check rate limits
        allowed, message = key_obj.check_rate_limit()
        if not allowed:
            return jsonify({"error": "Rate limit exceeded", "message": message}), 429

        # Record usage
        start_time = datetime.utcnow()
        response = f(key_obj, *args, **kwargs)
        end_time = datetime.utcnow()

        response_time = int((end_time - start_time).total_seconds() * 1000)
        key_obj.record_usage(request.endpoint, response_time)

        return response

    return decorated_function


# API Endpoints


@api_bp.route("/seo/meta-analysis", methods=["POST"])
@require_api_key
def api_meta_analysis(api_key):
    """API endpoint for meta tag analysis"""
    data = request.get_json()

    if not data or "url" not in data:
        return (
            jsonify(
                {
                    "error": "Missing required parameter",
                    "message": "URL parameter is required",
                }
            ),
            400,
        )

    url = data["url"]

    # Import the meta analysis utility
    from tools.utils.meta_tag_analyzer_utils import analyze_meta_tags

    try:
        results = analyze_meta_tags(url)
        return jsonify(
            {
                "success": True,
                "data": results,
                "usage": {
                    "remaining_daily": api_key.daily_limit
                    - APIUsage.get_daily_usage(api_key.api_key),
                    "plan": (
                        api_key.user.subscription.plan.name
                        if api_key.user.subscription
                        else "Free"
                    ),
                },
            }
        )
    except Exception as e:
        return jsonify({"error": "Analysis failed", "message": str(e)}), 500


@api_bp.route("/seo/broken-links", methods=["POST"])
@require_api_key
def api_broken_links(api_key):
    """API endpoint for broken link checking"""
    data = request.get_json()

    if not data or "url" not in data:
        return (
            jsonify(
                {
                    "error": "Missing required parameter",
                    "message": "URL parameter is required",
                }
            ),
            400,
        )

    from tools.utils.broken_link_checker_utils import check_broken_links

    try:
        results = check_broken_links(data["url"])
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"error": "Link check failed", "message": str(e)}), 500


@api_bp.route("/content/keywords", methods=["POST"])
@require_api_key
def api_keyword_analysis(api_key):
    """API endpoint for keyword analysis"""
    data = request.get_json()

    required_fields = ["url", "target_keyword"]
    if not all(field in data for field in required_fields):
        return (
            jsonify(
                {
                    "error": "Missing required parameters",
                    "message": f'Required fields: {", ".join(required_fields)}',
                }
            ),
            400,
        )

    from tools.utils.keyword_density_analyzer_utils import analyze_keyword_density

    try:
        results = analyze_keyword_density(data["url"], data["target_keyword"])
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"error": "Keyword analysis failed", "message": str(e)}), 500


@api_bp.route("/tools/list", methods=["GET"])
@require_api_key
def api_tools_list(api_key):
    """API endpoint to list available tools"""
    from tools.routes import all_tools

    available_tools = []
    for tool in all_tools:
        available_tools.append(
            {
                "name": tool["name"],
                "category": tool["category"],
                "description": tool["description"],
                "endpoint": f"/api/v1/tools/{tool['endpoint'].replace('.', '/')}",
            }
        )

    return jsonify(
        {
            "success": True,
            "data": {"total_tools": len(available_tools), "tools": available_tools},
        }
    )


# API Key Management Routes


@api_bp.route("/keys", methods=["GET"])
@login_required
def list_api_keys():
    """List user's API keys"""
    keys = APIKey.query.filter_by(user_id=current_user.id).all()

    return jsonify(
        {
            "success": True,
            "data": [
                {
                    "id": key.id,
                    "name": key.key_name,
                    "api_key": key.api_key[:8] + "...",  # Masked key
                    "permissions": key.permissions,
                    "daily_limit": key.daily_limit,
                    "is_active": key.is_active,
                    "created_at": key.created_at.isoformat(),
                    "last_used": key.last_used.isoformat() if key.last_used else None,
                }
                for key in keys
            ],
        }
    )


@api_bp.route("/keys", methods=["POST"])
@login_required
def create_api_key():
    """Create new API key"""
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Key name required"}), 400

    # Check user's subscription limits
    user_keys_count = APIKey.query.filter_by(user_id=current_user.id).count()

    # Free users get 1 API key, paid users get more
    max_keys = 1
    if current_user.subscription and current_user.subscription.is_active():
        max_keys = 5 if current_user.subscription.plan.name == "Pro" else 10

    if user_keys_count >= max_keys:
        return (
            jsonify(
                {
                    "error": "API key limit reached",
                    "message": f"Maximum {max_keys} keys allowed for your plan",
                }
            ),
            400,
        )

    # Create new API key
    api_key = APIKey(
        user_id=current_user.id,
        key_name=data["name"],
        permissions=data.get("permissions", []),
        daily_limit=data.get("daily_limit", 1000),
    )
    api_key.generate_key()

    db.session.add(api_key)
    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "id": api_key.id,
                    "name": api_key.key_name,
                    "api_key": api_key.api_key,
                    "api_secret": api_key.api_secret,
                    "message": "Store these credentials securely. The secret will not be shown again.",
                },
            }
        ),
        201,
    )


@api_bp.route("/keys/<int:key_id>", methods=["DELETE"])
@login_required
def delete_api_key(key_id):
    """Delete API key"""
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()

    if not api_key:
        return jsonify({"error": "API key not found"}), 404

    db.session.delete(api_key)
    db.session.commit()

    return jsonify({"success": True, "message": "API key deleted successfully"})
