"""
API versioning and documentation utilities.
"""

from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any, List, Optional
import inspect
from datetime import datetime


class APIVersioning:
    """API versioning manager."""

    def __init__(self):
        self.versions = {}
        self.deprecated_versions = set()

    def register_version(
        self, version: str, blueprint: Blueprint, deprecated: bool = False
    ):
        """Register API version."""
        self.versions[version] = blueprint
        if deprecated:
            self.deprecated_versions.add(version)

    def get_version_from_request(self) -> str:
        """Extract API version from request."""
        # Try header first
        version = request.headers.get("API-Version")
        if version:
            return version

        # Try URL path
        path_parts = request.path.split("/")
        if (
            len(path_parts) > 2
            and path_parts[1] == "api"
            and path_parts[2].startswith("v")
        ):
            return path_parts[2]

        # Default to latest
        return "v1"

    def is_deprecated(self, version: str) -> bool:
        """Check if version is deprecated."""
        return version in self.deprecated_versions


# Global API versioning instance
api_versioning = APIVersioning()


def versioned_api(version: str, deprecated: bool = False):
    """Decorator for versioned API endpoints."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            request_version = api_versioning.get_version_from_request()

            # Check if requested version matches
            if request_version != version:
                return (
                    jsonify(
                        {
                            "error": "API version mismatch",
                            "requested": request_version,
                            "available": version,
                        }
                    ),
                    400,
                )

            # Add deprecation warning
            if deprecated:
                response = f(*args, **kwargs)
                if isinstance(response, tuple):
                    data, status_code = response
                    if isinstance(data, dict):
                        data["warning"] = f"API version {version} is deprecated"
                    return data, status_code
                elif hasattr(response, "headers"):
                    response.headers["Warning"] = f"API version {version} is deprecated"

            return f(*args, **kwargs)

        return decorated_function

    return decorator


class APIDocGenerator:
    """Generate API documentation automatically."""

    def __init__(self):
        self.endpoints = {}

    def document_endpoint(self, func, method: str, path: str, version: str = "v1"):
        """Document an API endpoint."""
        doc = inspect.getdoc(func) or "No description available"
        signature = inspect.signature(func)

        self.endpoints[f"{method.upper()} {path}"] = {
            "function": func.__name__,
            "method": method.upper(),
            "path": path,
            "version": version,
            "description": doc,
            "parameters": self._extract_parameters(signature),
            "module": func.__module__,
        }

    def _extract_parameters(self, signature):
        """Extract parameter information from function signature."""
        params = []
        for name, param in signature.parameters.items():
            if name in ["self", "args", "kwargs"]:
                continue

            param_info = {
                "name": name,
                "type": (
                    str(param.annotation) if param.annotation != param.empty else "Any"
                ),
                "required": param.default == param.empty,
                "default": str(param.default) if param.default != param.empty else None,
            }
            params.append(param_info)

        return params

    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": current_app.config.get("SITE_NAME", "API"),
                "version": "1.0.0",
                "description": "Auto-generated API documentation",
            },
            "servers": [
                {"url": current_app.config.get("SITE_URL", "http://localhost:5000")}
            ],
            "paths": {},
        }

        for endpoint_key, endpoint_info in self.endpoints.items():
            path = endpoint_info["path"]
            method = endpoint_info["method"].lower()

            if path not in spec["paths"]:
                spec["paths"][path] = {}

            spec["paths"][path][method] = {
                "summary": endpoint_info["description"].split("\n")[0],
                "description": endpoint_info["description"],
                "parameters": [
                    {
                        "name": param["name"],
                        "in": "query",
                        "required": param["required"],
                        "schema": {"type": "string"},  # Simplified
                    }
                    for param in endpoint_info["parameters"]
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }

        return spec


# Global documentation generator
doc_generator = APIDocGenerator()


def document_api(method: str, path: str, version: str = "v1"):
    """Decorator to automatically document API endpoints."""

    def decorator(f):
        doc_generator.document_endpoint(f, method, path, version)
        return f

    return decorator


def create_api_blueprint(version: str = "v1") -> Blueprint:
    """Create versioned API blueprint with documentation endpoint."""
    api_bp = Blueprint(f"api_{version}", __name__, url_prefix=f"/api/{version}")

    @api_bp.route("/docs")
    def api_docs():
        """API documentation endpoint."""
        return jsonify(doc_generator.generate_openapi_spec())

    @api_bp.route("/health")
    def health_check():
        """Health check endpoint."""
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": version,
            }
        )

    return api_bp


class ResponseFormatter:
    """Standardized API response formatting."""

    @staticmethod
    def success(
        data: Any = None, message: str = None, meta: Dict = None
    ) -> Dict[str, Any]:
        """Format successful response."""
        response = {"success": True, "timestamp": datetime.utcnow().isoformat()}

        if data is not None:
            response["data"] = data

        if message:
            response["message"] = message

        if meta:
            response["meta"] = meta

        return response

    @staticmethod
    def error(message: str, code: str = None, details: Any = None) -> Dict[str, Any]:
        """Format error response."""
        response = {
            "success": False,
            "error": {"message": message, "timestamp": datetime.utcnow().isoformat()},
        }

        if code:
            response["error"]["code"] = code

        if details:
            response["error"]["details"] = details

        return response

    @staticmethod
    def paginated(
        data: List[Any], page: int, per_page: int, total: int
    ) -> Dict[str, Any]:
        """Format paginated response."""
        return ResponseFormatter.success(
            data=data,
            meta={
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page,
                }
            },
        )
