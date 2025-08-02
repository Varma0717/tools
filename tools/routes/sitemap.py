from flask import Blueprint, current_app, url_for, render_template, Response
from datetime import datetime

sitemap_bp = Blueprint('sitemap', __name__, url_prefix='')

@sitemap_bp.route('/sitemap.xml', methods=['GET'])
def sitemap_xml():
    """
    Dynamically generate an XML sitemap by introspecting app.url_map,
    skipping admin, user, and Google-login routes.
    """
    pages = []
    today = datetime.utcnow().date().isoformat()

    for rule in current_app.url_map.iter_rules():
        # Skip any internal/admin/user/auth routes
        if (
            rule.rule.startswith('/admin') or
            rule.rule.startswith('/users') or
            rule.rule.startswith('/auth/google') or
            rule.rule.startswith('/login/google')
        ):
            continue

        # Only include public GET routes without URL params
        if (
            "GET" in rule.methods and
            len(rule.arguments) == 0 and
            rule.endpoint != 'static'
        ):
            loc = url_for(rule.endpoint, _external=True)
            pages.append({
                'loc': loc,
                'lastmod': today,
                'changefreq': 'weekly',
                'priority': '0.5'
            })

    xml = render_template('sitemap.xml', pages=pages)
    return Response(xml, mimetype='application/xml')
