import re

def minify_html(html: str) -> tuple[str | None, str | None]:
    try:
        # Remove comments except IE conditional ones
        html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)

        # Remove line breaks and extra whitespace between tags
        html = re.sub(r'>\s+<', '><', html)

        # Remove leading/trailing whitespace
        html = re.sub(r'\s{2,}', ' ', html)
        html = html.strip()

        return html, None
    except Exception as e:
        return None, f"HTML Minification Error: {str(e)}"
