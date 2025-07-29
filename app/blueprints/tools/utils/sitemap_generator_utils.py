import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

def generate_sitemap_xml(seed_url: str, max_pages: int = 100) -> tuple[str | None, str | None]:
    visited = set()
    queue = deque([seed_url])
    domain = urlparse(seed_url).netloc

    urls = []

    try:
        while queue and len(visited) < max_pages:
            url = queue.popleft()
            if url in visited:
                continue

            try:
                res = requests.get(url, timeout=5)
                if res.status_code != 200 or "text/html" not in res.headers.get("Content-Type", ""):
                    continue

                soup = BeautifulSoup(res.text, "html.parser")
                visited.add(url)
                urls.append(url)

                for link in soup.find_all("a", href=True):
                    href = link.get("href")
                    abs_url = urljoin(url, href)
                    parsed = urlparse(abs_url)

                    if parsed.netloc != domain or parsed.scheme not in ["http", "https"]:
                        continue

                    clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path
                    if clean_url not in visited:
                        queue.append(clean_url)

            except Exception:
                continue

        # Build XML
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in sorted(set(urls)):
            xml += f"  <url><loc>{u}</loc></url>\n"
        xml += '</urlset>'
        return xml, None

    except Exception as e:
        return None, f"Sitemap generation failed: {str(e)}"
