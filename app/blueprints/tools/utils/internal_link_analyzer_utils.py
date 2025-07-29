import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def extract_internal_links(url: str, timeout: int = 10) -> list[dict]:
    try:
        domain = urlparse(url).netloc
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        seen = set()

        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)

            if parsed.netloc == domain:
                norm_url = parsed.scheme + "://" + parsed.netloc + parsed.path
                if norm_url not in seen:
                    seen.add(norm_url)
                    links.append({
                        "url": norm_url,
                        "anchor": a.get_text(strip=True) or "(no text)"
                    })

        return links
    except Exception:
        return []
