import requests

def check_http_headers(url: str) -> tuple[dict | None, str | None]:
    try:
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        response = requests.get(url, timeout=10)
        headers = dict(response.headers)
        headers['Status-Code'] = str(response.status_code)
        headers['Final-URL'] = response.url
        return headers, None
    except requests.exceptions.RequestException as e:
        return None, f"Error: {str(e)}"
