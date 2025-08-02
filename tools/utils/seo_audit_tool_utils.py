import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def audit_seo(url: str) -> dict:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # Title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        title_length = len(title)

        # Meta description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag.get("content", "").strip() if desc_tag else ""
        description_length = len(description)

        # H1 tag
        h1_tag = soup.find("h1")
        has_h1 = bool(h1_tag)

        # Canonical tag
        canonical_tag = soup.find("link", rel="canonical")
        has_canonical = bool(canonical_tag and canonical_tag.get("href", ""))

        # ALT tags on images
        images = soup.find_all("img")
        total_images = len(images)
        images_with_alt = sum(1 for img in images if img.get("alt"))

        # Link types
        domain = urlparse(url).netloc
        internal_links = 0
        external_links = 0
        for a in soup.find_all("a", href=True):
            link = a["href"]
            if domain in link or link.startswith("/"):
                internal_links += 1
            else:
                external_links += 1

        return {
            "title": title,
            "title_length": title_length,
            "description": description,
            "description_length": description_length,
            "has_h1": has_h1,
            "has_canonical": has_canonical,
            "total_images": total_images,
            "images_with_alt": images_with_alt,
            "internal_links": internal_links,
            "external_links": external_links
        }
    except Exception:
        return {
            "error": "Unable to fetch or parse the page. Please check the URL."
        }
