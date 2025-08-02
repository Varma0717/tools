from flask import Blueprint, render_template, request

serp_snippet_preview_bp = Blueprint('serp_snippet_preview', __name__, url_prefix='/tools')

@serp_snippet_preview_bp.route('/serp-snippet-preview', methods=['GET', 'POST'], endpoint='serp_snippet_preview')
def serp_snippet_preview():
    values, warning = {}, {}
    if request.method == "POST":
        values['title'] = request.form.get("title", "").strip()
        values['url'] = request.form.get("url", "").strip()
        values['description'] = request.form.get("description", "").strip()
        warning = {
            "title": len(values['title']) > 60,
            "description": len(values['description']) > 160,
            "url": len(values['url']) > 75
        }
    return render_template('tools/serp_snippet_preview.html', values=values, warning=warning)
