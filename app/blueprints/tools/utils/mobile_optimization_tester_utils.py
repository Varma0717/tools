import requests
from bs4 import BeautifulSoup
import re

def test_mobile_optimization(url: str) -> dict:
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')

        # Viewport tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        has_viewport = bool(viewport and 'width=device-width' in viewport.get('content', ''))

        # Check for media queries in <style> or linked CSS
        media_queries = len(re.findall(r'@media\s*\((max|min)-width', html, re.IGNORECASE)) > 0

        # Check body width responsiveness (basic)
        body = soup.find('body')
        style_width = re.findall(r'width\s*:\s*\d+px', body.get_text()) if body else []
        is_responsive_width = not bool(style_width)

        # Check font-size declarations in style tags
        font_sizes = re.findall(r'font-size\s*:\s*(\d+)px', html, re.IGNORECASE)
        min_font_ok = all(int(px) >= 12 for px in font_sizes) if font_sizes else True

        # Calculate score
        score = sum([
            has_viewport,
            media_queries,
            is_responsive_width,
            min_font_ok
        ]) * 25

        return {
            "viewport": has_viewport,
            "media_queries": media_queries,
            "responsive_width": is_responsive_width,
            "font_size_ok": min_font_ok,
            "score": score
        }
    except Exception:
        return {
            "viewport": False,
            "media_queries": False,
            "responsive_width": False,
            "font_size_ok": False,
            "score": 0
        }
