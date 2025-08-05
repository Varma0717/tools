from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user
import requests
from urllib.parse import urljoin, urlparse
import re
import time
from datetime import datetime
import json
from utils.professional_decorators import openrouter_api_tool, pro_subscription_required

ai_technical_seo_audit_bp = Blueprint("ai_technical_seo_audit", __name__)


@ai_technical_seo_audit_bp.route("/ai-technical-seo-audit")
@openrouter_api_tool
@pro_subscription_required
def ai_technical_seo_audit():
    """AI-powered technical SEO audit requiring Pro subscription"""
    return render_template("tools/ai_technical_seo_audit.html")


@ai_technical_seo_audit_bp.route("/ai-technical-seo-audit", methods=["POST"])
@openrouter_api_tool
@pro_subscription_required
def ai_technical_seo_audit_post():
    """Process AI technical SEO audit with comprehensive analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Perform comprehensive technical SEO analysis
        audit_results = perform_technical_seo_audit(url)

        # Generate AI-powered insights and recommendations
        ai_insights = generate_ai_technical_insights(audit_results, url)

        # Calculate overall technical SEO score
        technical_score = calculate_technical_seo_score(audit_results)

        return jsonify(
            {
                "success": True,
                "url": url,
                "audit_results": audit_results,
                "ai_insights": ai_insights,
                "technical_score": technical_score,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


def perform_technical_seo_audit(url):
    """Perform comprehensive technical SEO audit"""
    results = {
        "basic_analysis": {},
        "performance": {},
        "crawlability": {},
        "indexability": {},
        "mobile_optimization": {},
        "security": {},
        "technical_issues": [],
    }

    try:
        # Basic page analysis
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

        results["basic_analysis"] = {
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "final_url": response.url,
            "redirects": len(response.history),
            "content_type": response.headers.get("content-type", ""),
            "server": response.headers.get("server", ""),
            "content_length": len(response.content),
        }

        # Parse HTML content
        content = response.text

        # Performance analysis
        results["performance"] = analyze_performance_factors(content, response)

        # Crawlability analysis
        results["crawlability"] = analyze_crawlability(content, url)

        # Indexability analysis
        results["indexability"] = analyze_indexability(content, response)

        # Mobile optimization
        results["mobile_optimization"] = analyze_mobile_optimization(content)

        # Security analysis
        results["security"] = analyze_security_factors(response, url)

        # Technical issues detection
        results["technical_issues"] = detect_technical_issues(content, response, url)

    except Exception as e:
        results["error"] = str(e)

    return results


def analyze_performance_factors(content, response):
    """Analyze performance-related factors"""
    perf_data = {
        "page_size": len(content),
        "compression": "gzip" in response.headers.get("content-encoding", ""),
        "caching": {},
        "resources": {},
        "core_web_vitals": {},
    }

    # Cache analysis
    cache_control = response.headers.get("cache-control", "")
    perf_data["caching"] = {
        "cache_control": cache_control,
        "expires": response.headers.get("expires", ""),
        "last_modified": response.headers.get("last-modified", ""),
        "etag": response.headers.get("etag", ""),
        "cacheable": "no-cache" not in cache_control.lower(),
    }

    # Resource analysis
    css_links = re.findall(
        r'<link[^>]*href=[\'"](.*?\.css[^\'\"]*)', content, re.IGNORECASE
    )
    js_scripts = re.findall(
        r'<script[^>]*src=[\'"](.*?\.js[^\'\"]*)', content, re.IGNORECASE
    )
    images = re.findall(r'<img[^>]*src=[\'"](.*?)[\'"]', content, re.IGNORECASE)

    perf_data["resources"] = {
        "css_files": len(css_links),
        "js_files": len(js_scripts),
        "images": len(images),
        "external_css": sum(1 for css in css_links if "http" in css),
        "external_js": sum(1 for js in js_scripts if "http" in js),
        "inline_styles": content.count("<style"),
        "inline_scripts": content.count("<script>") + content.count("<script "),
    }

    # Basic Core Web Vitals estimation
    perf_data["core_web_vitals"] = {
        "estimated_lcp": estimate_lcp_from_content(content),
        "potential_cls_issues": detect_cls_issues(content),
        "render_blocking_resources": len(css_links)
        + len(
            [
                js
                for js in js_scripts
                if "defer" not in content and "async" not in content
            ]
        ),
    }

    return perf_data


def analyze_crawlability(content, url):
    """Analyze crawlability factors"""
    crawl_data = {
        "robots_meta": {},
        "internal_links": 0,
        "external_links": 0,
        "navigation": {},
        "url_structure": {},
    }

    # Robots meta analysis
    robots_match = re.search(
        r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)',
        content,
        re.IGNORECASE,
    )
    if robots_match:
        robots_content = robots_match.group(1).lower()
        crawl_data["robots_meta"] = {
            "content": robots_content,
            "noindex": "noindex" in robots_content,
            "nofollow": "nofollow" in robots_content,
            "noarchive": "noarchive" in robots_content,
            "nosnippet": "nosnippet" in robots_content,
        }

    # Link analysis
    all_links = re.findall(r'<a[^>]*href=[\'"](.*?)[\'"]', content, re.IGNORECASE)
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    for link in all_links:
        if link.startswith("http"):
            if domain in link:
                crawl_data["internal_links"] += 1
            else:
                crawl_data["external_links"] += 1
        elif link.startswith("/") or not link.startswith(("mailto:", "tel:", "#")):
            crawl_data["internal_links"] += 1

    # Navigation analysis
    crawl_data["navigation"] = {
        "has_nav_tag": "<nav" in content.lower(),
        "breadcrumbs": "breadcrumb" in content.lower(),
        "sitemap_link": "sitemap" in content.lower(),
        "footer_links": content.lower().count("<footer") > 0,
    }

    # URL structure analysis
    crawl_data["url_structure"] = {
        "url_length": len(url),
        "has_parameters": "?" in url,
        "has_fragments": "#" in url,
        "depth": url.count("/") - 2,  # Subtract protocol slashes
        "uses_hyphens": "-" in url,
        "uses_underscores": "_" in url,
    }

    return crawl_data


def analyze_indexability(content, response):
    """Analyze indexability factors"""
    index_data = {
        "meta_tags": {},
        "duplicate_content": {},
        "content_quality": {},
        "structured_data": {},
    }

    # Meta tags analysis
    title_match = re.search(
        r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL
    )
    desc_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)',
        content,
        re.IGNORECASE,
    )

    index_data["meta_tags"] = {
        "has_title": bool(title_match),
        "title_length": len(title_match.group(1).strip()) if title_match else 0,
        "has_description": bool(desc_match),
        "description_length": len(desc_match.group(1)) if desc_match else 0,
        "has_keywords": 'name="keywords"' in content.lower(),
    }

    # Canonical URL analysis
    canonical_match = re.search(
        r'<link[^>]*rel=["\']canonical["\']\s+href=["\']([^"\']+)',
        content,
        re.IGNORECASE,
    )
    index_data["canonical"] = {
        "has_canonical": bool(canonical_match),
        "canonical_url": canonical_match.group(1) if canonical_match else None,
    }

    # Structured data analysis
    json_ld_count = content.count("application/ld+json")
    microdata_count = content.count("itemscope")

    index_data["structured_data"] = {
        "json_ld_scripts": json_ld_count,
        "microdata_items": microdata_count,
        "has_schema": json_ld_count > 0 or microdata_count > 0,
    }

    # Content quality analysis
    text_content = re.sub(r"<[^>]+>", " ", content)
    word_count = len(text_content.split())

    index_data["content_quality"] = {
        "word_count": word_count,
        "heading_tags": {
            "h1": content.count("<h1"),
            "h2": content.count("<h2"),
            "h3": content.count("<h3"),
            "h4": content.count("<h4"),
            "h5": content.count("<h5"),
            "h6": content.count("<h6"),
        },
        "images_with_alt": len(
            re.findall(r'<img[^>]*alt=[\'"][^\'\"]*[\'"]', content, re.IGNORECASE)
        ),
        "total_images": content.count("<img"),
    }

    return index_data


def analyze_mobile_optimization(content):
    """Analyze mobile optimization factors"""
    mobile_data = {"viewport": {}, "responsive_design": {}, "mobile_usability": {}}

    # Viewport analysis
    viewport_match = re.search(
        r'<meta\s+name=["\']viewport["\']\s+content=["\']([^"\']+)',
        content,
        re.IGNORECASE,
    )
    if viewport_match:
        viewport_content = viewport_match.group(1)
        mobile_data["viewport"] = {
            "has_viewport": True,
            "content": viewport_content,
            "width_device": "width=device-width" in viewport_content,
            "initial_scale": "initial-scale=1" in viewport_content,
            "user_scalable": "user-scalable=no" not in viewport_content,
        }
    else:
        mobile_data["viewport"] = {"has_viewport": False}

    # Responsive design indicators
    mobile_data["responsive_design"] = {
        "has_media_queries": "@media" in content,
        "flexible_images": "max-width:100%" in content or "max-width: 100%" in content,
        "css_frameworks": any(
            framework in content.lower()
            for framework in ["bootstrap", "foundation", "bulma", "tailwind"]
        ),
        "responsive_units": "rem" in content
        or "em" in content
        or "vw" in content
        or "vh" in content,
    }

    # Mobile usability factors
    mobile_data["mobile_usability"] = {
        "tap_targets": content.count("button") + content.count('type="button"'),
        "readable_font_size": "font-size" in content,
        "adequate_spacing": "padding" in content or "margin" in content,
        "horizontal_scrolling": "overflow-x" in content,
    }

    return mobile_data


def analyze_security_factors(response, url):
    """Analyze security factors"""
    security_data = {"https": {}, "headers": {}, "vulnerabilities": []}

    # HTTPS analysis
    security_data["https"] = {
        "uses_https": url.startswith("https://"),
        "strict_transport_security": "strict-transport-security" in response.headers,
        "mixed_content_risk": url.startswith("https://") and "http://" in response.text,
    }

    # Security headers analysis
    security_headers = {
        "x-frame-options": response.headers.get("x-frame-options"),
        "x-content-type-options": response.headers.get("x-content-type-options"),
        "x-xss-protection": response.headers.get("x-xss-protection"),
        "content-security-policy": response.headers.get("content-security-policy"),
        "referrer-policy": response.headers.get("referrer-policy"),
    }

    security_data["headers"] = {
        "present": {k: v is not None for k, v in security_headers.items()},
        "values": security_headers,
    }

    # Basic vulnerability checks
    content = response.text.lower()
    if "eval(" in content:
        security_data["vulnerabilities"].append(
            "Potential XSS risk: eval() function detected"
        )
    if "document.write(" in content:
        security_data["vulnerabilities"].append(
            "Potential XSS risk: document.write() detected"
        )
    if not security_data["https"]["uses_https"]:
        security_data["vulnerabilities"].append(
            "Security risk: Website not using HTTPS"
        )

    return security_data


def detect_technical_issues(content, response, url):
    """Detect various technical SEO issues"""
    issues = []

    # Performance issues
    if len(content) > 2000000:  # 2MB
        issues.append(
            {
                "type": "Performance",
                "severity": "High",
                "issue": "Large page size detected",
                "description": f"Page size is {len(content)/1024:.1f}KB. Consider optimizing.",
                "impact": "Slower loading times affect user experience and rankings",
            }
        )

    # SEO issues
    if response.status_code != 200:
        issues.append(
            {
                "type": "SEO",
                "severity": "Critical",
                "issue": f"HTTP {response.status_code} error",
                "description": "Page returns error status code",
                "impact": "Search engines cannot index the page",
            }
        )

    # Meta tag issues
    if "<title>" not in content.lower():
        issues.append(
            {
                "type": "SEO",
                "severity": "Critical",
                "issue": "Missing title tag",
                "description": "Page has no title tag",
                "impact": "Critical for search engine rankings",
            }
        )

    title_count = content.lower().count("<title>")
    if title_count > 1:
        issues.append(
            {
                "type": "SEO",
                "severity": "High",
                "issue": "Multiple title tags",
                "description": f"Found {title_count} title tags",
                "impact": "Confuses search engines about page topic",
            }
        )

    # Check for missing meta description
    if 'name="description"' not in content.lower():
        issues.append(
            {
                "type": "SEO",
                "severity": "Medium",
                "issue": "Missing meta description",
                "description": "Page has no meta description",
                "impact": "Missed opportunity for better SERP presentation",
            }
        )

    # H1 tag analysis
    h1_count = content.lower().count("<h1")
    if h1_count == 0:
        issues.append(
            {
                "type": "SEO",
                "severity": "Medium",
                "issue": "Missing H1 tag",
                "description": "Page has no H1 heading",
                "impact": "Important for content hierarchy and SEO",
            }
        )
    elif h1_count > 1:
        issues.append(
            {
                "type": "SEO",
                "severity": "Medium",
                "issue": "Multiple H1 tags",
                "description": f"Found {h1_count} H1 tags",
                "impact": "Best practice is one H1 per page",
            }
        )

    # Mobile issues
    if 'name="viewport"' not in content.lower():
        issues.append(
            {
                "type": "Mobile",
                "severity": "High",
                "issue": "Missing viewport meta tag",
                "description": "Page lacks mobile viewport configuration",
                "impact": "Poor mobile user experience",
            }
        )

    # Image issues
    images_without_alt = len(re.findall(r"<img(?![^>]*alt=)", content, re.IGNORECASE))
    if images_without_alt > 0:
        issues.append(
            {
                "type": "Accessibility",
                "severity": "Medium",
                "issue": "Images missing alt text",
                "description": f"{images_without_alt} images without alt attributes",
                "impact": "Poor accessibility and missed SEO opportunities",
            }
        )

    return issues


def estimate_lcp_from_content(content):
    """Estimate Largest Contentful Paint based on content"""
    # Simple estimation based on content size and complexity
    content_size = len(content)
    if content_size < 100000:  # 100KB
        return "Good (< 2.5s estimated)"
    elif content_size < 500000:  # 500KB
        return "Needs Improvement (2.5-4s estimated)"
    else:
        return "Poor (> 4s estimated)"


def detect_cls_issues(content):
    """Detect potential Cumulative Layout Shift issues"""
    cls_issues = []

    # Check for images without dimensions
    img_without_dimensions = re.findall(
        r"<img(?![^>]*(?:width|height)=)", content, re.IGNORECASE
    )
    if img_without_dimensions:
        cls_issues.append("Images without explicit dimensions")

    # Check for web fonts without font-display
    if "@font-face" in content and "font-display" not in content:
        cls_issues.append("Web fonts without font-display property")

    # Check for dynamic content insertion
    if "async" in content.lower() or "defer" in content.lower():
        cls_issues.append("Potential async content loading")

    return cls_issues


def generate_ai_technical_insights(audit_results, url):
    """Generate AI-powered technical insights using OpenRouter API"""
    try:
        import os
        import requests

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return generate_fallback_technical_insights(audit_results, url)

        # Prepare audit summary for AI analysis
        audit_summary = f"""
        Technical SEO Audit Summary for {url}:
        
        Performance:
        - Page size: {audit_results.get('basic_analysis', {}).get('content_length', 0)} bytes
        - Response time: {audit_results.get('basic_analysis', {}).get('response_time', 0):.2f}s
        - Compression: {'Enabled' if audit_results.get('performance', {}).get('compression') else 'Disabled'}
        - CSS files: {audit_results.get('performance', {}).get('resources', {}).get('css_files', 0)}
        - JS files: {audit_results.get('performance', {}).get('resources', {}).get('js_files', 0)}
        
        SEO:
        - Title tag: {'Present' if audit_results.get('indexability', {}).get('meta_tags', {}).get('has_title') else 'Missing'}
        - Meta description: {'Present' if audit_results.get('indexability', {}).get('meta_tags', {}).get('has_description') else 'Missing'}
        - Word count: {audit_results.get('indexability', {}).get('content_quality', {}).get('word_count', 0)}
        - H1 tags: {audit_results.get('indexability', {}).get('content_quality', {}).get('heading_tags', {}).get('h1', 0)}
        
        Mobile:
        - Viewport tag: {'Present' if audit_results.get('mobile_optimization', {}).get('viewport', {}).get('has_viewport') else 'Missing'}
        - Responsive design: {'Detected' if audit_results.get('mobile_optimization', {}).get('responsive_design', {}).get('has_media_queries') else 'Not detected'}
        
        Security:
        - HTTPS: {'Enabled' if audit_results.get('security', {}).get('https', {}).get('uses_https') else 'Disabled'}
        - Security headers: {sum(1 for v in audit_results.get('security', {}).get('headers', {}).get('present', {}).values() if v)} present
        
        Technical Issues: {len(audit_results.get('technical_issues', []))} issues found
        """

        prompt = f"""As a technical SEO expert, analyze this comprehensive audit and provide actionable insights:

{audit_summary}

Provide detailed recommendations in these areas:
1. Performance Optimization (specific actions to improve Core Web Vitals)
2. Technical SEO Improvements (crawling, indexing, structure)
3. Mobile Experience Enhancement
4. Security Implementation
5. Priority Action Items (what to fix first)

Focus on technical implementation details that developers can act on immediately."""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1500,
                "temperature": 0.7,
            },
            timeout=30,
        )

        if response.status_code == 200:
            ai_response = response.json()
            insights = ai_response["choices"][0]["message"]["content"]

            return {
                "ai_powered": True,
                "insights": insights,
                "recommendations": parse_ai_recommendations(insights),
                "model_used": "meta-llama/llama-3.1-8b-instruct",
            }

    except Exception as e:
        print(f"AI analysis error: {e}")

    return generate_fallback_technical_insights(audit_results, url)


def generate_fallback_technical_insights(audit_results, url):
    """Generate fallback insights when AI is unavailable"""
    recommendations = []

    # Performance recommendations
    perf = audit_results.get("performance", {})
    if not perf.get("compression"):
        recommendations.append(
            {
                "category": "Performance",
                "priority": "High",
                "action": "Enable GZIP/Brotli compression",
                "description": "Reduce file sizes by enabling server compression",
            }
        )

    resources = perf.get("resources", {})
    if resources.get("css_files", 0) > 5:
        recommendations.append(
            {
                "category": "Performance",
                "priority": "Medium",
                "action": "Optimize CSS delivery",
                "description": f'Consider combining {resources.get("css_files")} CSS files',
            }
        )

    if resources.get("js_files", 0) > 5:
        recommendations.append(
            {
                "category": "Performance",
                "priority": "Medium",
                "action": "Optimize JavaScript loading",
                "description": f'Consider bundling {resources.get("js_files")} JS files',
            }
        )

    # SEO recommendations
    indexability = audit_results.get("indexability", {})
    meta_tags = indexability.get("meta_tags", {})

    if not meta_tags.get("has_title"):
        recommendations.append(
            {
                "category": "SEO",
                "priority": "Critical",
                "action": "Add title tag",
                "description": "Every page must have a unique, descriptive title tag",
            }
        )

    if not meta_tags.get("has_description"):
        recommendations.append(
            {
                "category": "SEO",
                "priority": "High",
                "action": "Add meta description",
                "description": "Write compelling meta descriptions for better click-through rates",
            }
        )

    content_quality = indexability.get("content_quality", {})
    h1_count = content_quality.get("heading_tags", {}).get("h1", 0)
    if h1_count == 0:
        recommendations.append(
            {
                "category": "SEO",
                "priority": "Medium",
                "action": "Add H1 heading",
                "description": "Every page should have exactly one H1 tag",
            }
        )
    elif h1_count > 1:
        recommendations.append(
            {
                "category": "SEO",
                "priority": "Medium",
                "action": "Fix multiple H1 tags",
                "description": f"Use only one H1 tag per page (found {h1_count})",
            }
        )

    # Mobile recommendations
    mobile = audit_results.get("mobile_optimization", {})
    if not mobile.get("viewport", {}).get("has_viewport"):
        recommendations.append(
            {
                "category": "Mobile",
                "priority": "High",
                "action": "Add viewport meta tag",
                "description": 'Add <meta name="viewport" content="width=device-width, initial-scale=1">',
            }
        )

    # Security recommendations
    security = audit_results.get("security", {})
    if not security.get("https", {}).get("uses_https"):
        recommendations.append(
            {
                "category": "Security",
                "priority": "Critical",
                "action": "Implement HTTPS",
                "description": "Migrate to HTTPS for security and SEO benefits",
            }
        )

    headers_present = security.get("headers", {}).get("present", {})
    missing_headers = [k for k, v in headers_present.items() if not v]
    if missing_headers:
        recommendations.append(
            {
                "category": "Security",
                "priority": "Medium",
                "action": "Add security headers",
                "description": f'Implement missing headers: {", ".join(missing_headers)}',
            }
        )

    return {
        "ai_powered": False,
        "insights": f"""Professional Technical SEO Analysis for {url}:

Based on the comprehensive audit, your website shows several areas for optimization. 
The analysis covers performance, SEO fundamentals, mobile optimization, and security factors.

Key findings include performance optimization opportunities, SEO structural improvements,
mobile experience enhancements, and security implementations that should be prioritized.

This professional analysis provides actionable recommendations ranked by priority and impact.""",
        "recommendations": recommendations,
        "model_used": "Professional Algorithm Analysis",
    }


def parse_ai_recommendations(insights):
    """Parse AI insights into structured recommendations"""
    recommendations = []

    # Basic parsing of AI response into actionable items
    lines = insights.split("\n")
    current_category = "General"

    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ["performance", "optimization"]):
            current_category = "Performance"
        elif any(keyword in line.lower() for keyword in ["seo", "search"]):
            current_category = "SEO"
        elif any(keyword in line.lower() for keyword in ["mobile", "responsive"]):
            current_category = "Mobile"
        elif any(keyword in line.lower() for keyword in ["security", "https"]):
            current_category = "Security"

        if line.startswith(("-", "•", "*")) or line.lower().startswith(
            ("implement", "add", "optimize", "fix")
        ):
            recommendations.append(
                {
                    "category": current_category,
                    "priority": "Medium",
                    "action": line.lstrip("-•* "),
                    "description": "AI-recommended optimization",
                }
            )

    return recommendations


def calculate_technical_seo_score(audit_results):
    """Calculate overall technical SEO score"""
    score = 0
    max_score = 100

    # Performance scoring (25 points)
    perf = audit_results.get("performance", {})
    if perf.get("compression"):
        score += 5

    resources = perf.get("resources", {})
    if resources.get("css_files", 0) <= 3:
        score += 5
    if resources.get("js_files", 0) <= 3:
        score += 5
    if resources.get("external_css", 0) <= 1:
        score += 5
    if resources.get("external_js", 0) <= 1:
        score += 5

    # SEO fundamentals scoring (30 points)
    indexability = audit_results.get("indexability", {})
    meta_tags = indexability.get("meta_tags", {})

    if meta_tags.get("has_title"):
        score += 8
    if meta_tags.get("has_description"):
        score += 6
    if 30 <= meta_tags.get("title_length", 0) <= 60:
        score += 4
    if 120 <= meta_tags.get("description_length", 0) <= 160:
        score += 4

    content_quality = indexability.get("content_quality", {})
    h1_count = content_quality.get("heading_tags", {}).get("h1", 0)
    if h1_count == 1:
        score += 4
    if content_quality.get("word_count", 0) >= 300:
        score += 4

    # Mobile optimization scoring (20 points)
    mobile = audit_results.get("mobile_optimization", {})
    viewport = mobile.get("viewport", {})
    if viewport.get("has_viewport"):
        score += 8
    if viewport.get("width_device"):
        score += 4
    if mobile.get("responsive_design", {}).get("has_media_queries"):
        score += 8

    # Security scoring (15 points)
    security = audit_results.get("security", {})
    if security.get("https", {}).get("uses_https"):
        score += 8
    headers_count = sum(
        1 for v in security.get("headers", {}).get("present", {}).values() if v
    )
    score += min(7, headers_count * 1.4)

    # Technical issues penalty (10 points)
    issues = audit_results.get("technical_issues", [])
    critical_issues = sum(1 for issue in issues if issue.get("severity") == "Critical")
    high_issues = sum(1 for issue in issues if issue.get("severity") == "High")

    penalty = (critical_issues * 5) + (high_issues * 2)
    score = max(0, score - penalty)

    # Calculate percentage
    percentage = min(100, (score / max_score) * 100)

    # Determine grade
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": round(percentage, 1),
        "grade": grade,
        "points_earned": score,
        "max_points": max_score,
        "breakdown": {
            "performance": min(25, score * 0.25),
            "seo_fundamentals": min(30, score * 0.30),
            "mobile_optimization": min(20, score * 0.20),
            "security": min(15, score * 0.15),
            "technical_issues": min(10, 10 - penalty),
        },
    }
