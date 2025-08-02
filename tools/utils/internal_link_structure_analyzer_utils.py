import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def analyze_internal_structure(base_url: str, timeout: int = 10) -> list[dict]:
    results = []
    try:
        domain = urlparse(base_url).netloc
        res = requests.get(base_url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, 'html.parser')

        seen = set()
        for a in soup.find_all('a', href=True):
            href = urljoin(base_url, a['href'].strip())
            parsed = urlparse(href)
            if parsed.netloc != domain:
                continue
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean_url not in seen:
                seen.add(clean_url)
                results.append({
                    "from": base_url,
                    "to": clean_url,
                    "anchor": a.get_text(strip=True) or "(no text)"
                })

        return results
    except Exception:
        return []
