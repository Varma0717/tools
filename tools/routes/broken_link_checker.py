# tools/routes/broken_link_checker.py

from flask import Blueprint, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests

broken_link_checker_bp = Blueprint('broken_link_checker', __name__, url_prefix='/tools')

def check_link_status(link):
    try:
        resp = requests.head(link, timeout=6, allow_redirects=True)
        status_code = resp.status_code
        if status_code in [200, 201, 204]:
            return 'Working', status_code
        else:
            return 'Broken', status_code
    except Exception:
        return 'Broken', 'Timeout/Error'

def extract_links(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        anchors = soup.find_all('a', href=True)
        links = []
        for a in anchors:
            href = a['href']
            if href.startswith('http'):
                links.append({'link': href, 'source': url})
        return links
    except Exception:
        return []

@broken_link_checker_bp.route('/broken-link-checker', methods=['GET', 'POST'])
def broken_link_checker():
    report, stats, error = [], {"total": 0, "broken": 0, "working": 0}, None
    if request.method == "POST":
        url = request.form.get("url", "")
        if not url.startswith("http"):
            url = "https://" + url
        try:
            links = extract_links(url)
            working = broken = 0
            for link_data in links:
                status, code = check_link_status(link_data['link'])
                if status == 'Working':
                    working += 1
                else:
                    broken += 1
                report.append({
                    'source': link_data['source'],
                    'link': link_data['link'],
                    'status': status,
                    'code': code
                })
            stats = {
                'total': len(report),
                'working': working,
                'broken': broken
            }
        except Exception as e:
            error = f"Failed to check links: {str(e)}"
    return render_template("tools/broken_link_checker.html", report=report, stats=stats, error=error)

import traceback

@broken_link_checker_bp.route('/broken-link-checker/ajax', methods=['POST'])
def broken_link_checker_ajax():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        if not url.startswith('http'):
            return jsonify({'error': 'Invalid URL'}), 400

        links = extract_links(url)
        if not links:
            return jsonify({'error': 'No links found on the page.'}), 200

        report = []
        working = broken = 0

        for link_data in links:
            status, code = check_link_status(link_data['link'])
            if status == 'Working':
                working += 1
            else:
                broken += 1
            report.append({
                'source': link_data['source'],
                'link': link_data['link'],
                'status': status,
                'code': code
            })

        stats = {
            'total': len(report),
            'working': working,
            'broken': broken
        }
        return jsonify({'stats': stats, 'report': report})
    except Exception as e:
        print("[BrokenLinkCheckerAjax] Error:", e)
        print(traceback.format_exc())
        return jsonify({'error': 'Sorry, something went wrong. Please try again.'}), 500
