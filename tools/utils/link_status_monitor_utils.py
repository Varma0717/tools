import requests

def check_link_status(urls: list[str], timeout: int = 5) -> list[dict]:
    results = []
    for url in urls:
        url = url.strip()
        if not url:
            continue

        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            status = response.status_code
        except requests.exceptions.RequestException:
            status = None

        results.append({
            "url": url,
            "status_code": status if status else "Error",
            "status_label": (
                "OK" if status == 200 else
                "Redirected" if status in (301, 302) else
                "Not Found" if status == 404 else
                "Error" if not status else
                f"HTTP {status}"
            )
        })
    return results
