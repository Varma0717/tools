import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def test_website_speed(url: str, timeout: int = 10) -> tuple[dict | None, str | None]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        start = time.time()
        response = requests.get(url, timeout=timeout, headers=headers)
        end = time.time()

        if not response.ok:
            return None, f"Request failed with status {response.status_code}"

        html = response.text
        total_time = round((end - start) * 1000)  # ms
        total_size = len(response.content)

        soup = BeautifulSoup(html, "html.parser")
        domain = urlparse(url).netloc

        resource_urls = set()
        for tag in soup.find_all(["img", "script", "link"]):
            src = tag.get("src") or tag.get("href")
            if src:
                full_url = urljoin(url, src)
                if domain in full_url:
                    resource_urls.add(full_url)

        slow_resources = []
        for res_url in list(resource_urls)[:25]:
            try:
                res_start = time.time()
                res = requests.get(res_url, timeout=5)
                res_end = time.time()
                res_time = round((res_end - res_start) * 1000)
                if res_time > 500:
                    slow_resources.append((res_url, res_time))
            except:
                continue

        return {
            "url": url,
            "load_time_ms": total_time,
            "page_size_kb": round(total_size / 1024, 2),
            "resource_count": len(resource_urls),
            "slow_resources": slow_resources
        }, None

    except Exception as e:
        return None, str(e)
