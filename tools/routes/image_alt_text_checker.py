from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
from bs4 import BeautifulSoup

image_alt_text_checker_bp = Blueprint('image_alt_text_checker', __name__, url_prefix='/tools')

@image_alt_text_checker_bp.route('/image-alt-text-checker', methods=['GET'])
def image_alt_text_checker():
    csrf_token = generate_csrf()
    return render_template('tools/image_alt_text_checker.html', csrf_token=csrf_token)

@image_alt_text_checker_bp.route('/image-alt-text-checker/ajax', methods=['POST'])
def image_alt_text_checker_ajax():
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    csrf_token = request.headers.get('X-CSRFToken', '')
    try:
        validate_csrf(csrf_token)
    except Exception:
        return jsonify({'error': 'CSRF token missing or invalid.'}), 400
    
    if not url:
        return jsonify({'error': 'Please enter a valid page URL.'}), 400
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
    except Timeout:
        return jsonify({'error': 'The request timed out. The website might be too slow or unreachable.'}), 200
    except ConnectionError:
        return jsonify({'error': 'Could not connect to the URL. Please verify the website is online and accessible.'}), 200
    except RequestException as e:
        return jsonify({'error': f'An error occurred while fetching the URL: {str(e)}'}), 200

    try:
        soup = BeautifulSoup(resp.text, 'html.parser')
        imgs = []
        for img in soup.find_all('img'):
            src = img.get('src') or ''
            alt = img.get('alt') or ''
            imgs.append({'src': src, 'alt': alt})
        
        if not imgs:
            return jsonify({'warning': 'No images found on this page.'}), 200

        return jsonify({'images': imgs}), 200
    except Exception as e:
        return jsonify({'error': f'Error processing the page content: {str(e)}'}), 200
