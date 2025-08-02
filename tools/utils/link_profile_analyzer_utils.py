import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def analyze_link_profile(page_url: str) -> dict:
    domain = urlparse(page_url).netloc
    try:
        response = requests.get(page_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')

        internal = []
        external = []

        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            full_url = urljoin(page_url, href)
            anchor = a.get_text(strip=True) or "(no text)"
            rel = a.get("rel", [])
            is_nofollow = 'nofollow' in rel

            link_data = {
                "url": full_url,
                "anchor": anchor,
                "rel": "nofollow" if is_nofollow else "dofollow"
            }

            if urlparse(full_url).netloc == domain:
                internal.append(link_data)
            else:
                external.append(link_data)

        return {
            "internal": internal,
            "external": external
        }
    except Exception:
        return {
            "internal": [],
            "external": []
        }
