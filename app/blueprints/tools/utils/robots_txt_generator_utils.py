def generate_robots_txt(data: dict) -> tuple[str | None, str | None]:
    try:
        agent = data.get("agent", "*").strip()
        allow_paths = data.get("allow", "").splitlines()
        disallow_paths = data.get("disallow", "").splitlines()
        sitemap_url = data.get("sitemap", "").strip()
        crawl_delay = data.get("crawl_delay", "").strip()

        lines = [f"User-agent: {agent}"]

        for path in disallow_paths:
            if path.strip():
                lines.append(f"Disallow: {path.strip()}")

        for path in allow_paths:
            if path.strip():
                lines.append(f"Allow: {path.strip()}")

        if crawl_delay:
            lines.append(f"Crawl-delay: {crawl_delay}")

        if sitemap_url:
            lines.append(f"Sitemap: {sitemap_url}")

        return "\n".join(lines), None
    except Exception as e:
        return None, f"Error generating robots.txt: {str(e)}"
