import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import ssl
import socket

def run_site_audit(url):
    audit = {
        "status_code": None,
        "load_time": None,
        "title": "",
        "meta_description": "",
        "canonical": "",
        "robots_meta": "",
        "h1_count": 0,
        "h2_count": 0,
        "internal_links": 0,
        "external_links": 0,
        "images": 0,
        "missing_alt_images": 0,
        "broken_images": 0,
        "word_count": 0,
        "content_length": 0,
        "headers": {},
        "ssl_valid": False,
    }

    try:
        start = time.time()
        response = requests.get(url, timeout=10, headers={"User-Agent": "SEO-AuditBot"})
        load_time = time.time() - start

        audit["status_code"] = response.status_code
        audit["load_time"] = round(load_time, 2)
        audit["headers"] = dict(response.headers)
        audit["content_length"] = len(response.text)
        audit["word_count"] = len(response.text.split())

        soup = BeautifulSoup(response.text, 'html.parser')

        # Meta tags
        audit["title"] = (soup.title.string.strip() if soup.title else "")
        meta_desc = soup.find("meta", attrs={"name": "description"})
        audit["meta_description"] = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""

        canonical = soup.find("link", rel="canonical")
        audit["canonical"] = canonical["href"].strip() if canonical and canonical.get("href") else ""

        robots = soup.find("meta", attrs={"name": "robots"})
        audit["robots_meta"] = robots["content"].strip() if robots and robots.get("content") else ""

        # Heading tags
        audit["h1_count"] = len(soup.find_all("h1"))
        audit["h2_count"] = len(soup.find_all("h2"))

        # Link audit
        internal_links = 0
        external_links = 0
        base_domain = urlparse(url).netloc

        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']
            parsed_href = urlparse(urljoin(url, href))
            if parsed_href.netloc == base_domain:
                internal_links += 1
            else:
                external_links += 1

        audit["internal_links"] = internal_links
        audit["external_links"] = external_links

        # Image audit
        images = soup.find_all("img")
        audit["images"] = len(images)
        audit["missing_alt_images"] = len([img for img in images if not img.get("alt")])

        broken_images = 0
        for img in images:
            img_src = img.get("src")
            if img_src:
                img_url = urljoin(url, img_src)
                try:
                    img_res = requests.head(img_url, timeout=5)
                    if img_res.status_code >= 400:
                        broken_images += 1
                except:
                    broken_images += 1

        audit["broken_images"] = broken_images

        # SSL Check
        try:
            hostname = urlparse(url).hostname
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname):
                    audit["ssl_valid"] = True
        except:
            audit["ssl_valid"] = False

        return audit

    except Exception as e:
        return {"error": str(e)}
