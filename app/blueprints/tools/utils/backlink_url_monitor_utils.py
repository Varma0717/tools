import requests
from bs4 import BeautifulSoup

def monitor_backlinks(target: str, urls: list[str], timeout: int = 10) -> list[dict]:
    results = []
    target = target.strip().rstrip('/')
    
    for source_url in urls:
        source_url = source_url.strip()
        if not source_url:
            continue

        found = False
        anchor_text = "N/A"
        try:
            res = requests.get(source_url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, 'html.parser')
            anchors = soup.find_all('a', href=True)
            for a in anchors:
                href = a['href'].strip().rstrip('/')
                if href.startswith(target):
                    found = True
                    anchor_text = a.get_text(strip=True) or "(no text)"
                    break
        except Exception:
            pass

        results.append({
            "source_url": source_url,
            "status": "Found" if found else "Not Found",
            "anchor_text": anchor_text if found else "-"
        })

    return results
