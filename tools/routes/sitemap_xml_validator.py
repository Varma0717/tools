# tools/routes/sitemap_xml_validator.py

from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
import requests
from xml.etree import ElementTree
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

sitemap_xml_validator_bp = Blueprint('sitemap_xml_validator', __name__, url_prefix='/tools')

COMMON_SITEMAP_PATHS = [
    '/sitemap.xml',
    '/sitemap_index.xml',
    '/wp-sitemap.xml',
    '/sitemap1.xml',
    '/sitemap-main.xml',
]

def validate_sitemap(xml_content):
    if not xml_content.strip():
        return {"valid": False, "error": "No XML content provided."}
    try:
        root = ElementTree.fromstring(xml_content)
        if root.tag.endswith('urlset'):
            urls = [url.find("{*}loc").text for url in root.findall("{*}url") if url.find("{*}loc") is not None]
            return {"valid": True, "type": "urlset", "urls": urls, "count": len(urls)}
        elif root.tag.endswith('sitemapindex'):
            sitemaps = [sm.find("{*}loc").text for sm in root.findall("{*}sitemap") if sm.find("{*}loc") is not None]
            return {"valid": True, "type": "sitemapindex", "sitemaps": sitemaps, "count": len(sitemaps)}
        else:
            return {"valid": False, "error": "Unknown sitemap structure."}
    except Exception as e:
        return {"valid": False, "error": f"Could not parse XML: {e}"}

def try_fetch_sitemaps(base_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    for path in COMMON_SITEMAP_PATHS:
        sm_url = base_url.rstrip('/') + path
        try:
            r = requests.get(sm_url, timeout=7, headers=headers)
            if r.status_code == 200 and r.text.strip().startswith('<?xml'):
                # Check structure
                root = ElementTree.fromstring(r.text)
                if root.tag.endswith('sitemapindex'):
                    sitemap_urls = [
                        el.find("{*}loc").text
                        for el in root.findall("{*}sitemap")
                        if el.find("{*}loc") is not None
                    ]
                    return {'type': 'sitemapindex', 'content': r.text, 'sitemaps': sitemap_urls, 'main_url': sm_url}
                elif root.tag.endswith('urlset'):
                    return {'type': 'urlset', 'content': r.text, 'main_url': sm_url}
        except Exception:
            continue
    return None

def crawl_site(base_url, max_pages=200):
    seen, to_crawl = set(), set([base_url])
    urls = []
    domain = urlparse(base_url).netloc
    headers = {"User-Agent": "Mozilla/5.0"}
    while to_crawl and len(urls) < max_pages:
        url = to_crawl.pop()
        try:
            resp = requests.get(url, headers=headers, timeout=7)
            if not resp.ok or 'text/html' not in resp.headers.get('Content-Type', ''):
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            urls.append(url)
            for link in soup.find_all('a', href=True):
                href = urljoin(url, link['href'])
                href_parsed = urlparse(href)
                if (
                    href_parsed.netloc == domain
                    and href.startswith("http")
                    and href not in seen
                    and '#' not in href_parsed.path
                    and not any(href_parsed.path.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".zip", ".rar", ".svg", ".ico", ".mp4", ".webp"])
                ):
                    seen.add(href)
                    to_crawl.add(href)
        except Exception:
            continue
    return list(dict.fromkeys(urls))  # dedupe, preserve order

@sitemap_xml_validator_bp.route('/sitemap-xml-validator', methods=['GET'])
def sitemap_xml_validator():
    csrf_token = generate_csrf()
    return render_template('tools/sitemap_xml_validator.html', csrf_token=csrf_token)

@sitemap_xml_validator_bp.route('/sitemap-xml-validator/ajax', methods=['POST'])
def sitemap_xml_validator_ajax():
    data = request.get_json()
    url = data.get('url', '').strip()
    sitemap_xml = data.get('sitemap_xml', '').strip()
    csrf_token = request.headers.get("X-CSRFToken", "")
    try:
        validate_csrf(csrf_token)
    except Exception:
        return jsonify({"error": "CSRF token missing or invalid."}), 400

    # 1. If XML provided, validate it
    if sitemap_xml:
        result = validate_sitemap(sitemap_xml)
        result["fetched_xml"] = sitemap_xml
        return jsonify(result)

    # 2. If URL provided, try known sitemaps
    if url:
        result = try_fetch_sitemaps(url)
        if result:
            if result['type'] == 'urlset':
                valid = validate_sitemap(result['content'])
                valid['fetched_xml'] = result['content']
                valid['sitemap_url'] = result['main_url']
                return jsonify(valid)
            elif result['type'] == 'sitemapindex':
                # Fetch all child sitemaps and aggregate URLs
                all_urls = []
                for sm_url in result['sitemaps']:
                    try:
                        sm_resp = requests.get(sm_url, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
                        if sm_resp.status_code == 200:
                            sm_valid = validate_sitemap(sm_resp.text)
                            if sm_valid.get('urls'):
                                all_urls.extend(sm_valid['urls'])
                    except Exception:
                        continue
                return jsonify({
                    "valid": True,
                    "type": "sitemapindex",
                    "sitemaps": result['sitemaps'],
                    "all_urls": all_urls,
                    "count": len(all_urls),
                    "fetched_xml": result['content'],
                    "sitemap_url": result['main_url']
                })

        # 3. If no sitemap found, crawl and generate
        crawled_urls = crawl_site(url, max_pages=200)
        if not crawled_urls:
            return jsonify({"error": "Could not fetch any sitemap.xml or crawl the site. The site may be offline, blocking bots, or has no crawlable links."}), 200
        # Generate sitemap.xml
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in crawled_urls:
            xml += f'  <url><loc>{u}</loc></url>\n'
        xml += '</urlset>'
        return jsonify({
            "generated": xml,
            "valid": True,
            "type": "urlset",
            "urls": crawled_urls,
            "count": len(crawled_urls)
        })

    # 4. If neither provided, show template
    generated = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n'
        '    <loc>https://yourdomain.com/</loc>\n'
        '    <priority>1.0</priority>\n'
        '  </url>\n'
        '</urlset>'
    )
    return jsonify({"generated": generated})
