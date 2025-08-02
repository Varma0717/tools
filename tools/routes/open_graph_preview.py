from flask import Blueprint, render_template, request, jsonify

from bs4 import BeautifulSoup

from flask_wtf.csrf import generate_csrf, validate_csrf

import requests



open_graph_preview_bp = Blueprint('open_graph_preview', __name__, url_prefix='/tools')



@open_graph_preview_bp.route('/open-graph-preview', methods=['GET'])

def open_graph_preview():

    csrf_token = generate_csrf()

    return render_template('tools/open_graph_preview.html') 



@open_graph_preview_bp.route('/open-graph-preview/ajax', methods=['POST'])

def open_graph_preview_ajax():

    try:

        validate_csrf(request.headers.get("X-CSRFToken"))

    except Exception:

        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400



    data = request.get_json()

    url = data.get("url", "").strip()

    if not url:

        return jsonify({"success": False, "error": "Please enter a valid URL."}), 400

    if not url.startswith("http"):

        url = "https://" + url



    try:

        headers = {"User-Agent": "Mozilla/5.0"}

        resp = requests.get(url, headers=headers, timeout=15)

        soup = BeautifulSoup(resp.text, "html.parser")



        preview = {

            'title': soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'twitter:title'}),

            'description': soup.find('meta', property='og:description') or soup.find('meta', attrs={'name': 'twitter:description'}),

            'image': soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'twitter:image'}),

            'site_name': soup.find('meta', property='og:site_name'),

            'url': soup.find('meta', property='og:url'),

            'twitter_card': soup.find('meta', attrs={'name': 'twitter:card'}),

        }



        for k, v in preview.items():

            if v and hasattr(v, 'get'):

                preview[k] = v.get('content', '') or v.get('href', '')

            else:

                preview[k] = ''

        return jsonify({"success": True, "preview": preview})

    except Exception as e:

        return jsonify({"success": False, "error": f"Error fetching data: {str(e)}"}), 500

