from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError
from models.page_view import PageView
from utils.extensions import db
from datetime import datetime

page_view_counter_bp = Blueprint('page_view_counter', __name__, url_prefix='/tools/page-view-counter')

@page_view_counter_bp.route('/')
def page_view_counter():
    return render_template('tools/page_view_counter.html')

@page_view_counter_bp.route('/ajax', methods=['POST'])
def page_view_counter_ajax():
    try:
        csrf_token = request.headers.get('X-CSRFToken') or request.json.get('csrf_token')
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    data = request.get_json() or {}
    page_slug = data.get('page_slug', '').strip()
    if not page_slug:
        return jsonify({"error": "Please enter a page slug or URL."}), 400

    # Normalize slug (strip protocol, domain if URL given)
    if page_slug.startswith('http'):
        from urllib.parse import urlparse
        parsed = urlparse(page_slug)
        page_slug = parsed.path.strip('/')

    page_view = PageView.query.filter_by(page_slug=page_slug).first()
    view_count = page_view.view_count if page_view else 0

    return jsonify({
        "page_slug": page_slug,
        "view_count": view_count,
        "last_viewed_at": page_view.last_viewed_at.isoformat() if page_view else None
    })
