from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user
import requests
from urllib.parse import urljoin, urlparse
import re
import time
from datetime import datetime
import json
from bs4 import BeautifulSoup
from utils.professional_decorators import openrouter_api_tool, pro_subscription_required

ai_performance_optimizer_bp = Blueprint("ai_performance_optimizer", __name__)


@ai_performance_optimizer_bp.route("/ai-performance-optimizer")
@openrouter_api_tool
@pro_subscription_required
def ai_performance_optimizer():
    """AI-powered performance optimization requiring Pro subscription"""
    return render_template("tools/ai_performance_optimizer.html")


@ai_performance_optimizer_bp.route("/ai-performance-optimizer", methods=["POST"])
@openrouter_api_tool
@pro_subscription_required
def ai_performance_optimizer_post():
    """Process AI performance optimization with comprehensive analysis"""
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

        # Perform comprehensive performance analysis
        performance_analysis = analyze_website_performance(url)

        # Generate Core Web Vitals assessment
        core_web_vitals = assess_core_web_vitals(performance_analysis, url)

        # Analyze resource optimization opportunities
        resource_optimization = analyze_resource_optimization(performance_analysis)

        # Generate AI-powered optimization recommendations
        ai_recommendations = generate_ai_performance_recommendations(
            performance_analysis, core_web_vitals, resource_optimization, url
        )

        # Calculate performance score
        performance_score = calculate_performance_score(
            performance_analysis, core_web_vitals
        )

        return jsonify(
            {
                "success": True,
                "url": url,
                "performance_analysis": performance_analysis,
                "core_web_vitals": core_web_vitals,
                "resource_optimization": resource_optimization,
                "ai_recommendations": ai_recommendations,
                "performance_score": performance_score,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


def analyze_website_performance(url):
    """Perform comprehensive performance analysis"""
    analysis = {
        "basic_metrics": {},
        "resource_analysis": {},
        "server_analysis": {},
        "content_analysis": {},
        "caching_analysis": {},
        "compression_analysis": {},
        "code_optimization": {},
        "image_optimization": {},
    }

    try:
        start_time = time.time()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        end_time = time.time()

        # Basic performance metrics
        analysis["basic_metrics"] = {
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "total_size": len(response.content),
            "compressed_size": int(
                response.headers.get("content-length", len(response.content))
            ),
            "compression_ratio": calculate_compression_ratio(response),
            "redirects": len(response.history),
            "final_url": response.url,
        }

        if response.status_code == 200:
            content = response.text
            soup = BeautifulSoup(content, "html.parser")

            # Resource analysis
            analysis["resource_analysis"] = analyze_page_resources(content, soup, url)

            # Server analysis
            analysis["server_analysis"] = analyze_server_performance(response)

            # Content analysis
            analysis["content_analysis"] = analyze_content_performance(content, soup)

            # Caching analysis
            analysis["caching_analysis"] = analyze_caching_strategy(response)

            # Compression analysis
            analysis["compression_analysis"] = analyze_compression_optimization(
                response, content
            )

            # Code optimization analysis
            analysis["code_optimization"] = analyze_code_optimization(content, soup)

            # Image optimization analysis
            analysis["image_optimization"] = analyze_image_optimization(soup, url)

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


def calculate_compression_ratio(response):
    """Calculate compression ratio if available"""
    if "content-encoding" in response.headers:
        original_size = len(response.content)
        compressed_size = int(response.headers.get("content-length", original_size))
        if compressed_size > 0:
            return ((original_size - compressed_size) / original_size) * 100
    return 0


def analyze_page_resources(content, soup, base_url):
    """Analyze page resources for performance impact"""
    resources = {
        "css_files": [],
        "js_files": [],
        "images": [],
        "fonts": [],
        "external_resources": [],
        "resource_counts": {},
        "blocking_resources": [],
        "optimization_opportunities": [],
    }

    # CSS Files
    css_links = soup.find_all("link", rel="stylesheet")
    for css in css_links:
        href = css.get("href", "")
        if href:
            resources["css_files"].append(
                {
                    "url": href,
                    "is_external": href.startswith("http") and base_url not in href,
                    "is_blocking": True,  # CSS is render-blocking by default
                    "has_media_query": bool(css.get("media")),
                }
            )

    # JavaScript Files
    js_scripts = soup.find_all("script", src=True)
    for js in js_scripts:
        src = js.get("src", "")
        if src:
            is_async = js.get("async") is not None
            is_defer = js.get("defer") is not None
            resources["js_files"].append(
                {
                    "url": src,
                    "is_external": src.startswith("http") and base_url not in src,
                    "is_blocking": not (is_async or is_defer),
                    "is_async": is_async,
                    "is_defer": is_defer,
                }
            )

    # Images
    images = soup.find_all("img")
    for img in images:
        src = img.get("src", "")
        if src:
            resources["images"].append(
                {
                    "url": src,
                    "has_alt": bool(img.get("alt")),
                    "has_lazy_loading": img.get("loading") == "lazy",
                    "has_width": bool(img.get("width")),
                    "has_height": bool(img.get("height")),
                    "format": get_image_format(src),
                }
            )

    # Web Fonts
    font_links = soup.find_all("link", href=True)
    for link in font_links:
        href = link.get("href", "")
        if "font" in href.lower() or "googleapis.com/css" in href:
            resources["fonts"].append(
                {
                    "url": href,
                    "has_display": "font-display" in content,
                    "preload": link.get("rel") == "preload",
                }
            )

    # Resource counts
    resources["resource_counts"] = {
        "total_css": len(resources["css_files"]),
        "total_js": len(resources["js_files"]),
        "total_images": len(resources["images"]),
        "total_fonts": len(resources["fonts"]),
        "external_css": sum(1 for css in resources["css_files"] if css["is_external"]),
        "external_js": sum(1 for js in resources["js_files"] if js["is_external"]),
        "blocking_js": sum(1 for js in resources["js_files"] if js["is_blocking"]),
    }

    # Blocking resources
    resources["blocking_resources"] = [
        css for css in resources["css_files"] if css["is_blocking"]
    ] + [js for js in resources["js_files"] if js["is_blocking"]]

    # Optimization opportunities
    if resources["resource_counts"]["total_css"] > 3:
        resources["optimization_opportunities"].append(
            {
                "type": "CSS Optimization",
                "issue": f"Too many CSS files ({resources['resource_counts']['total_css']})",
                "recommendation": "Consider combining CSS files to reduce HTTP requests",
            }
        )

    if resources["resource_counts"]["blocking_js"] > 2:
        resources["optimization_opportunities"].append(
            {
                "type": "JavaScript Optimization",
                "issue": f"Too many blocking JS files ({resources['resource_counts']['blocking_js']})",
                "recommendation": "Add async/defer attributes to non-critical JavaScript",
            }
        )

    lazy_images = sum(1 for img in resources["images"] if img["has_lazy_loading"])
    if lazy_images < len(resources["images"]) * 0.8:
        resources["optimization_opportunities"].append(
            {
                "type": "Image Optimization",
                "issue": f"Only {lazy_images}/{len(resources['images'])} images use lazy loading",
                "recommendation": "Implement lazy loading for below-the-fold images",
            }
        )

    return resources


def get_image_format(url):
    """Determine image format from URL"""
    url_lower = url.lower()
    if ".webp" in url_lower:
        return "WebP"
    elif ".avif" in url_lower:
        return "AVIF"
    elif ".jpg" in url_lower or ".jpeg" in url_lower:
        return "JPEG"
    elif ".png" in url_lower:
        return "PNG"
    elif ".gif" in url_lower:
        return "GIF"
    elif ".svg" in url_lower:
        return "SVG"
    return "Unknown"


def analyze_server_performance(response):
    """Analyze server-side performance factors"""
    server_data = {
        "response_headers": {},
        "server_info": {},
        "performance_headers": {},
        "security_headers": {},
        "optimization_score": 0,
    }

    headers = response.headers

    # Server information
    server_data["server_info"] = {
        "server": headers.get("server", "Unknown"),
        "powered_by": headers.get("x-powered-by", "Unknown"),
        "content_type": headers.get("content-type", ""),
        "content_encoding": headers.get("content-encoding", ""),
        "transfer_encoding": headers.get("transfer-encoding", ""),
    }

    # Performance-related headers
    server_data["performance_headers"] = {
        "cache_control": headers.get("cache-control", ""),
        "expires": headers.get("expires", ""),
        "etag": headers.get("etag", ""),
        "last_modified": headers.get("last-modified", ""),
        "vary": headers.get("vary", ""),
        "connection": headers.get("connection", ""),
        "keep_alive": headers.get("keep-alive", ""),
    }

    # Security headers that affect performance
    server_data["security_headers"] = {
        "strict_transport_security": headers.get("strict-transport-security", ""),
        "content_security_policy": headers.get("content-security-policy", ""),
        "x_frame_options": headers.get("x-frame-options", ""),
        "x_content_type_options": headers.get("x-content-type-options", ""),
    }

    # Calculate optimization score
    score = 0

    # Compression
    if "gzip" in headers.get("content-encoding", "") or "br" in headers.get(
        "content-encoding", ""
    ):
        score += 20

    # Caching
    cache_control = headers.get("cache-control", "")
    if cache_control and "no-cache" not in cache_control:
        score += 20

    # HTTP/2
    if (
        hasattr(response, "raw")
        and hasattr(response.raw, "version")
        and response.raw.version == 20
    ):
        score += 15

    # Keep-alive
    if headers.get("connection", "").lower() == "keep-alive":
        score += 10

    # ETag
    if headers.get("etag"):
        score += 10

    # HTTPS
    if response.url.startswith("https://"):
        score += 15

    # CDN detection
    cdn_headers = ["cf-ray", "x-amz-cf-id", "x-cache", "x-served-by"]
    if any(header in headers for header in cdn_headers):
        score += 10

    server_data["optimization_score"] = score

    return server_data


def analyze_content_performance(content, soup):
    """Analyze content-related performance factors"""
    content_data = {
        "html_size": len(content),
        "dom_complexity": {},
        "critical_resources": {},
        "render_blocking": {},
        "optimization_opportunities": [],
    }

    # DOM complexity analysis
    all_elements = soup.find_all()
    content_data["dom_complexity"] = {
        "total_elements": len(all_elements),
        "depth": calculate_dom_depth(soup),
        "text_to_html_ratio": calculate_text_ratio(soup, content),
    }

    # Critical resources identification
    above_fold_images = 0
    critical_css = 0

    # Estimate above-the-fold content (simplified)
    first_images = soup.find_all("img")[:3]  # Assume first 3 images might be above fold
    for img in first_images:
        if not img.get("loading") == "lazy":
            above_fold_images += 1

    # Critical CSS detection
    style_tags = soup.find_all("style")
    for style in style_tags:
        if style.string and len(style.string) > 100:
            critical_css += 1

    content_data["critical_resources"] = {
        "above_fold_images": above_fold_images,
        "inline_critical_css": critical_css,
        "critical_css_size": sum(len(style.string or "") for style in style_tags),
    }

    # Render-blocking analysis
    css_links = soup.find_all("link", rel="stylesheet")
    js_scripts = soup.find_all("script", src=True)

    blocking_css = len(
        [css for css in css_links if not css.get("media") or css.get("media") == "all"]
    )
    blocking_js = len(
        [js for js in js_scripts if not js.get("async") and not js.get("defer")]
    )

    content_data["render_blocking"] = {
        "blocking_css_count": blocking_css,
        "blocking_js_count": blocking_js,
        "total_blocking_resources": blocking_css + blocking_js,
    }

    # Optimization opportunities
    if content_data["dom_complexity"]["total_elements"] > 1500:
        content_data["optimization_opportunities"].append(
            {
                "type": "DOM Optimization",
                "issue": f"High DOM complexity ({content_data['dom_complexity']['total_elements']} elements)",
                "recommendation": "Simplify HTML structure and remove unnecessary elements",
            }
        )

    if content_data["html_size"] > 500000:  # 500KB
        content_data["optimization_opportunities"].append(
            {
                "type": "HTML Size",
                "issue": f"Large HTML size ({content_data['html_size'] / 1024:.1f}KB)",
                "recommendation": "Minify HTML and remove unnecessary whitespace",
            }
        )

    if blocking_css > 2:
        content_data["optimization_opportunities"].append(
            {
                "type": "Render Blocking",
                "issue": f"Too many render-blocking CSS files ({blocking_css})",
                "recommendation": "Inline critical CSS and defer non-critical styles",
            }
        )

    return content_data


def calculate_dom_depth(element, depth=0):
    """Calculate maximum DOM depth"""
    if not element.children:
        return depth

    max_child_depth = depth
    for child in element.children:
        if hasattr(child, "children"):
            child_depth = calculate_dom_depth(child, depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

    return max_child_depth


def calculate_text_ratio(soup, content):
    """Calculate text to HTML ratio"""
    text_content = soup.get_text()
    text_length = len(text_content.strip())
    html_length = len(content)

    return (text_length / html_length * 100) if html_length > 0 else 0


def analyze_caching_strategy(response):
    """Analyze caching strategy and optimization"""
    caching_data = {"cache_headers": {}, "cache_score": 0, "recommendations": []}

    headers = response.headers

    # Cache-related headers
    caching_data["cache_headers"] = {
        "cache_control": headers.get("cache-control", ""),
        "expires": headers.get("expires", ""),
        "etag": headers.get("etag", ""),
        "last_modified": headers.get("last-modified", ""),
        "vary": headers.get("vary", ""),
        "pragma": headers.get("pragma", ""),
    }

    # Calculate cache score
    score = 0

    cache_control = headers.get("cache-control", "").lower()
    if cache_control:
        if "max-age" in cache_control:
            score += 30
        if "public" in cache_control:
            score += 15
        if "must-revalidate" in cache_control:
            score += 10
        if "no-cache" in cache_control or "no-store" in cache_control:
            score -= 20

    if headers.get("expires"):
        score += 20

    if headers.get("etag"):
        score += 20

    if headers.get("last-modified"):
        score += 15

    caching_data["cache_score"] = max(0, score)

    # Recommendations
    if not cache_control:
        caching_data["recommendations"].append(
            {
                "type": "Missing Cache Control",
                "recommendation": "Add Cache-Control header with appropriate max-age value",
            }
        )

    if "no-cache" in cache_control:
        caching_data["recommendations"].append(
            {
                "type": "Aggressive No-Cache",
                "recommendation": "Consider allowing caching for static resources",
            }
        )

    if not headers.get("etag") and not headers.get("last-modified"):
        caching_data["recommendations"].append(
            {
                "type": "Missing Validation",
                "recommendation": "Add ETag or Last-Modified headers for cache validation",
            }
        )

    return caching_data


def analyze_compression_optimization(response, content):
    """Analyze compression optimization opportunities"""
    compression_data = {
        "current_compression": {},
        "compression_score": 0,
        "savings_potential": {},
        "recommendations": [],
    }

    headers = response.headers
    content_encoding = headers.get("content-encoding", "")

    # Current compression status
    compression_data["current_compression"] = {
        "enabled": bool(content_encoding),
        "type": content_encoding,
        "original_size": len(content),
        "compressed_size": int(headers.get("content-length", len(content))),
    }

    # Calculate compression score
    score = 0
    if content_encoding:
        if "br" in content_encoding:  # Brotli
            score = 100
        elif "gzip" in content_encoding:
            score = 80
        else:
            score = 40

    compression_data["compression_score"] = score

    # Estimate savings potential
    if (
        not content_encoding and len(content) > 1024
    ):  # If no compression and content > 1KB
        # Estimate potential savings (typical gzip compression ratio)
        estimated_savings = len(content) * 0.7  # 70% compression typical
        compression_data["savings_potential"] = {
            "estimated_savings_bytes": estimated_savings,
            "estimated_savings_percentage": 70,
            "potential_size_reduction": f"{estimated_savings / 1024:.1f}KB",
        }

    # Recommendations
    if not content_encoding:
        compression_data["recommendations"].append(
            {
                "type": "Enable Compression",
                "recommendation": "Enable Gzip or Brotli compression on the server",
            }
        )
    elif "gzip" in content_encoding:
        compression_data["recommendations"].append(
            {
                "type": "Upgrade Compression",
                "recommendation": "Consider upgrading to Brotli compression for better performance",
            }
        )

    return compression_data


def analyze_code_optimization(content, soup):
    """Analyze code optimization opportunities"""
    code_data = {"minification": {}, "optimization_score": 0, "recommendations": []}

    # Check for minification
    has_minified_css = ".min.css" in content
    has_minified_js = ".min.js" in content

    # Analyze inline styles and scripts
    inline_styles = soup.find_all("style")
    inline_scripts = soup.find_all("script", src=False)

    total_inline_css_size = sum(len(style.string or "") for style in inline_styles)
    total_inline_js_size = sum(len(script.string or "") for script in inline_scripts)

    code_data["minification"] = {
        "has_minified_css": has_minified_css,
        "has_minified_js": has_minified_js,
        "inline_css_count": len(inline_styles),
        "inline_js_count": len(inline_scripts),
        "total_inline_css_size": total_inline_css_size,
        "total_inline_js_size": total_inline_js_size,
    }

    # Calculate optimization score
    score = 0
    if has_minified_css:
        score += 25
    if has_minified_js:
        score += 25
    if total_inline_css_size < 2048:  # Less than 2KB inline CSS
        score += 25
    if total_inline_js_size < 2048:  # Less than 2KB inline JS
        score += 25

    code_data["optimization_score"] = score

    # Recommendations
    if not has_minified_css:
        code_data["recommendations"].append(
            {
                "type": "CSS Minification",
                "recommendation": "Minify CSS files to reduce file size",
            }
        )

    if not has_minified_js:
        code_data["recommendations"].append(
            {
                "type": "JavaScript Minification",
                "recommendation": "Minify JavaScript files to reduce file size",
            }
        )

    if total_inline_css_size > 4096:  # More than 4KB
        code_data["recommendations"].append(
            {
                "type": "Excessive Inline CSS",
                "recommendation": "Move large inline CSS to external files",
            }
        )

    if total_inline_js_size > 4096:  # More than 4KB
        code_data["recommendations"].append(
            {
                "type": "Excessive Inline JavaScript",
                "recommendation": "Move large inline JavaScript to external files",
            }
        )

    return code_data


def analyze_image_optimization(soup, base_url):
    """Analyze image optimization opportunities"""
    image_data = {
        "image_stats": {},
        "optimization_score": 0,
        "format_analysis": {},
        "recommendations": [],
    }

    images = soup.find_all("img")

    # Image statistics
    total_images = len(images)
    images_with_alt = sum(1 for img in images if img.get("alt"))
    images_with_lazy = sum(1 for img in images if img.get("loading") == "lazy")
    images_with_dimensions = sum(
        1 for img in images if img.get("width") and img.get("height")
    )

    image_data["image_stats"] = {
        "total_images": total_images,
        "images_with_alt": images_with_alt,
        "images_with_lazy_loading": images_with_lazy,
        "images_with_dimensions": images_with_dimensions,
        "alt_ratio": (images_with_alt / total_images * 100) if total_images > 0 else 0,
        "lazy_loading_ratio": (
            (images_with_lazy / total_images * 100) if total_images > 0 else 0
        ),
        "dimensions_ratio": (
            (images_with_dimensions / total_images * 100) if total_images > 0 else 0
        ),
    }

    # Format analysis
    format_counts = {}
    for img in images:
        src = img.get("src", "")
        format_type = get_image_format(src)
        format_counts[format_type] = format_counts.get(format_type, 0) + 1

    image_data["format_analysis"] = format_counts

    # Calculate optimization score
    score = 0
    if image_data["image_stats"]["alt_ratio"] > 90:
        score += 25
    if image_data["image_stats"]["lazy_loading_ratio"] > 80:
        score += 25
    if image_data["image_stats"]["dimensions_ratio"] > 90:
        score += 25
    if format_counts.get("WebP", 0) > 0 or format_counts.get("AVIF", 0) > 0:
        score += 25

    image_data["optimization_score"] = score

    # Recommendations
    if image_data["image_stats"]["alt_ratio"] < 80:
        image_data["recommendations"].append(
            {
                "type": "Missing Alt Attributes",
                "recommendation": f"Add alt attributes to {total_images - images_with_alt} images",
            }
        )

    if image_data["image_stats"]["lazy_loading_ratio"] < 70:
        image_data["recommendations"].append(
            {
                "type": "Implement Lazy Loading",
                "recommendation": f"Add lazy loading to {total_images - images_with_lazy} images",
            }
        )

    if image_data["image_stats"]["dimensions_ratio"] < 80:
        image_data["recommendations"].append(
            {
                "type": "Add Image Dimensions",
                "recommendation": f"Add width/height attributes to {total_images - images_with_dimensions} images",
            }
        )

    if (
        format_counts.get("WebP", 0) == 0
        and format_counts.get("JPEG", 0) + format_counts.get("PNG", 0) > 0
    ):
        image_data["recommendations"].append(
            {
                "type": "Modern Image Formats",
                "recommendation": "Convert images to WebP or AVIF format for better compression",
            }
        )

    return image_data


def assess_core_web_vitals(performance_analysis, url):
    """Assess Core Web Vitals based on analysis"""
    cwv_data = {
        "lcp_assessment": {},
        "fid_assessment": {},
        "cls_assessment": {},
        "overall_score": 0,
        "recommendations": [],
    }

    # Largest Contentful Paint (LCP) Assessment
    response_time = performance_analysis.get("basic_metrics", {}).get(
        "response_time", 999
    )
    page_size = performance_analysis.get("basic_metrics", {}).get("total_size", 0)
    blocking_resources = (
        performance_analysis.get("resource_analysis", {})
        .get("resource_counts", {})
        .get("blocking_js", 0)
    )

    # Estimate LCP based on available metrics
    estimated_lcp = (
        response_time + (page_size / 1000000) + (blocking_resources * 0.1)
    )  # Rough estimation

    if estimated_lcp <= 2.5:
        lcp_score = 100
        lcp_rating = "Good"
    elif estimated_lcp <= 4.0:
        lcp_score = 70
        lcp_rating = "Needs Improvement"
    else:
        lcp_score = 30
        lcp_rating = "Poor"

    cwv_data["lcp_assessment"] = {
        "estimated_lcp": estimated_lcp,
        "score": lcp_score,
        "rating": lcp_rating,
        "factors": {
            "server_response_time": response_time,
            "page_size_impact": page_size / 1000000,
            "blocking_resources": blocking_resources,
        },
    }

    # First Input Delay (FID) Assessment
    js_files = (
        performance_analysis.get("resource_analysis", {})
        .get("resource_counts", {})
        .get("total_js", 0)
    )
    blocking_js = (
        performance_analysis.get("resource_analysis", {})
        .get("resource_counts", {})
        .get("blocking_js", 0)
    )

    # Estimate FID risk based on JavaScript load
    if blocking_js == 0:
        fid_score = 100
        fid_rating = "Good"
    elif blocking_js <= 2:
        fid_score = 80
        fid_rating = "Good"
    elif blocking_js <= 5:
        fid_score = 60
        fid_rating = "Needs Improvement"
    else:
        fid_score = 30
        fid_rating = "Poor"

    cwv_data["fid_assessment"] = {
        "estimated_risk": (
            "High" if blocking_js > 3 else "Medium" if blocking_js > 1 else "Low"
        ),
        "score": fid_score,
        "rating": fid_rating,
        "factors": {
            "total_js_files": js_files,
            "blocking_js_files": blocking_js,
            "main_thread_impact": blocking_js * 10,  # Estimate
        },
    }

    # Cumulative Layout Shift (CLS) Assessment
    images_without_dimensions = performance_analysis.get("image_optimization", {}).get(
        "image_stats", {}
    ).get("total_images", 0) - performance_analysis.get("image_optimization", {}).get(
        "image_stats", {}
    ).get(
        "images_with_dimensions", 0
    )
    web_fonts = len(performance_analysis.get("resource_analysis", {}).get("fonts", []))

    cls_risk_factors = images_without_dimensions + (web_fonts * 0.5)

    if cls_risk_factors <= 1:
        cls_score = 100
        cls_rating = "Good"
    elif cls_risk_factors <= 3:
        cls_score = 70
        cls_rating = "Needs Improvement"
    else:
        cls_score = 40
        cls_rating = "Poor"

    cwv_data["cls_assessment"] = {
        "estimated_risk": (
            "High"
            if cls_risk_factors > 3
            else "Medium" if cls_risk_factors > 1 else "Low"
        ),
        "score": cls_score,
        "rating": cls_rating,
        "factors": {
            "images_without_dimensions": images_without_dimensions,
            "web_fonts_loaded": web_fonts,
            "layout_shift_risk": cls_risk_factors,
        },
    }

    # Overall Core Web Vitals score
    cwv_data["overall_score"] = (lcp_score + fid_score + cls_score) / 3

    # Recommendations for Core Web Vitals
    if lcp_rating != "Good":
        cwv_data["recommendations"].append(
            {
                "metric": "LCP",
                "recommendation": "Optimize server response times, reduce resource sizes, and eliminate render-blocking resources",
            }
        )

    if fid_rating != "Good":
        cwv_data["recommendations"].append(
            {
                "metric": "FID",
                "recommendation": "Minimize JavaScript execution time, split code, and use web workers for heavy computations",
            }
        )

    if cls_rating != "Good":
        cwv_data["recommendations"].append(
            {
                "metric": "CLS",
                "recommendation": "Add size attributes to images and videos, avoid inserting content above existing content",
            }
        )

    return cwv_data


def analyze_resource_optimization(performance_analysis):
    """Analyze resource optimization opportunities"""
    optimization_data = {
        "priority_optimizations": [],
        "quick_wins": [],
        "advanced_optimizations": [],
        "estimated_savings": {},
    }

    # Extract data from performance analysis
    resource_analysis = performance_analysis.get("resource_analysis", {})
    basic_metrics = performance_analysis.get("basic_metrics", {})
    caching_analysis = performance_analysis.get("caching_analysis", {})
    compression_analysis = performance_analysis.get("compression_analysis", {})

    # Priority optimizations (high impact, medium effort)
    if not compression_analysis.get("current_compression", {}).get("enabled"):
        savings = compression_analysis.get("savings_potential", {}).get(
            "estimated_savings_bytes", 0
        )
        optimization_data["priority_optimizations"].append(
            {
                "type": "Enable Compression",
                "impact": "High",
                "effort": "Medium",
                "savings": f"{savings / 1024:.1f}KB",
                "description": "Enable Gzip or Brotli compression for significant size reduction",
            }
        )

    blocking_js = resource_analysis.get("resource_counts", {}).get("blocking_js", 0)
    if blocking_js > 2:
        optimization_data["priority_optimizations"].append(
            {
                "type": "Eliminate Render Blocking JavaScript",
                "impact": "High",
                "effort": "Medium",
                "savings": f"{blocking_js * 100}ms estimated",
                "description": f"Add async/defer to {blocking_js} blocking JavaScript files",
            }
        )

    # Quick wins (medium impact, low effort)
    cache_score = caching_analysis.get("cache_score", 0)
    if cache_score < 50:
        optimization_data["quick_wins"].append(
            {
                "type": "Implement Browser Caching",
                "impact": "Medium",
                "effort": "Low",
                "description": "Add proper cache headers for static resources",
            }
        )

    images_without_lazy = resource_analysis.get("resource_counts", {}).get(
        "total_images", 0
    ) - performance_analysis.get("image_optimization", {}).get("image_stats", {}).get(
        "images_with_lazy_loading", 0
    )
    if images_without_lazy > 3:
        optimization_data["quick_wins"].append(
            {
                "type": "Implement Lazy Loading",
                "impact": "Medium",
                "effort": "Low",
                "description": f"Add lazy loading to {images_without_lazy} images",
            }
        )

    # Advanced optimizations (high impact, high effort)
    total_css = resource_analysis.get("resource_counts", {}).get("total_css", 0)
    if total_css > 5:
        optimization_data["advanced_optimizations"].append(
            {
                "type": "CSS Bundle Optimization",
                "impact": "High",
                "effort": "High",
                "description": f"Combine and optimize {total_css} CSS files",
            }
        )

    dom_elements = (
        performance_analysis.get("content_analysis", {})
        .get("dom_complexity", {})
        .get("total_elements", 0)
    )
    if dom_elements > 1500:
        optimization_data["advanced_optimizations"].append(
            {
                "type": "DOM Simplification",
                "impact": "High",
                "effort": "High",
                "description": f"Reduce DOM complexity from {dom_elements} elements",
            }
        )

    # Estimated savings calculation
    total_size = basic_metrics.get("total_size", 0)
    compression_savings = compression_analysis.get("savings_potential", {}).get(
        "estimated_savings_bytes", 0
    )

    optimization_data["estimated_savings"] = {
        "compression_savings": f"{compression_savings / 1024:.1f}KB",
        "caching_savings": "50-90% on repeat visits",
        "image_optimization": "20-50% on image sizes",
        "code_minification": "10-30% on code files",
    }

    return optimization_data


def generate_ai_performance_recommendations(
    performance_analysis, core_web_vitals, resource_optimization, url
):
    """Generate AI-powered performance recommendations"""
    try:
        import os
        import requests

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return generate_fallback_performance_recommendations(
                performance_analysis, core_web_vitals, resource_optimization
            )

        # Prepare performance analysis summary for AI
        basic_metrics = performance_analysis.get("basic_metrics", {})
        resource_analysis = performance_analysis.get("resource_analysis", {})
        cwv = core_web_vitals

        analysis_summary = f"""
        Website Performance Analysis for {url}:
        
        Core Metrics:
        - Response Time: {basic_metrics.get('response_time', 0):.2f}s
        - Page Size: {basic_metrics.get('total_size', 0) / 1024:.1f}KB
        - Compression: {'Enabled' if performance_analysis.get('compression_analysis', {}).get('current_compression', {}).get('enabled') else 'Disabled'}
        
        Resources:
        - CSS Files: {resource_analysis.get('resource_counts', {}).get('total_css', 0)}
        - JavaScript Files: {resource_analysis.get('resource_counts', {}).get('total_js', 0)}
        - Blocking JS: {resource_analysis.get('resource_counts', {}).get('blocking_js', 0)}
        - Images: {resource_analysis.get('resource_counts', {}).get('total_images', 0)}
        
        Core Web Vitals Assessment:
        - LCP: {cwv.get('lcp_assessment', {}).get('rating', 'Unknown')} ({cwv.get('lcp_assessment', {}).get('estimated_lcp', 0):.1f}s estimated)
        - FID: {cwv.get('fid_assessment', {}).get('rating', 'Unknown')} risk
        - CLS: {cwv.get('cls_assessment', {}).get('rating', 'Unknown')} risk
        - Overall CWV Score: {cwv.get('overall_score', 0):.1f}/100
        
        Optimization Opportunities:
        - Priority fixes: {len(resource_optimization.get('priority_optimizations', []))}
        - Quick wins: {len(resource_optimization.get('quick_wins', []))}
        - Advanced optimizations: {len(resource_optimization.get('advanced_optimizations', []))}
        """

        prompt = f"""As a web performance optimization expert, analyze this comprehensive performance audit and provide actionable recommendations:

{analysis_summary}

Please provide detailed, technical recommendations in these areas:

1. **Immediate Performance Fixes**: Critical issues that should be addressed first
2. **Core Web Vitals Optimization**: Specific strategies to improve LCP, FID, and CLS
3. **Resource Optimization**: How to optimize loading and delivery of assets
4. **Advanced Performance Strategies**: Long-term optimizations for sustained performance
5. **Implementation Roadmap**: Step-by-step plan prioritized by impact vs effort

Focus on technical implementation details that developers can immediately act upon, including specific techniques, tools, and best practices."""

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
            recommendations = ai_response["choices"][0]["message"]["content"]

            return {
                "ai_powered": True,
                "recommendations": recommendations,
                "structured_recommendations": parse_ai_performance_recommendations(
                    recommendations
                ),
                "model_used": "meta-llama/llama-3.1-8b-instruct",
            }

    except Exception as e:
        print(f"AI analysis error: {e}")

    return generate_fallback_performance_recommendations(
        performance_analysis, core_web_vitals, resource_optimization
    )


def generate_fallback_performance_recommendations(
    performance_analysis, core_web_vitals, resource_optimization
):
    """Generate fallback recommendations when AI is unavailable"""
    recommendations = []

    # Priority recommendations based on analysis
    priority_opts = resource_optimization.get("priority_optimizations", [])
    for opt in priority_opts:
        recommendations.append(
            {
                "category": "Critical Performance",
                "priority": "High",
                "action": opt["type"],
                "description": opt["description"],
                "expected_impact": opt.get("savings", "Significant improvement"),
            }
        )

    # Core Web Vitals recommendations
    cwv_recommendations = core_web_vitals.get("recommendations", [])
    for cwv_rec in cwv_recommendations:
        recommendations.append(
            {
                "category": f"Core Web Vitals ({cwv_rec['metric']})",
                "priority": "High",
                "action": f"Optimize {cwv_rec['metric']}",
                "description": cwv_rec["recommendation"],
                "expected_impact": "Improved user experience and SEO",
            }
        )

    # Quick wins
    quick_wins = resource_optimization.get("quick_wins", [])
    for win in quick_wins:
        recommendations.append(
            {
                "category": "Quick Wins",
                "priority": "Medium",
                "action": win["type"],
                "description": win["description"],
                "expected_impact": "Fast implementation with good results",
            }
        )

    # Compression recommendations
    compression_analysis = performance_analysis.get("compression_analysis", {})
    for comp_rec in compression_analysis.get("recommendations", []):
        recommendations.append(
            {
                "category": "Compression",
                "priority": "High",
                "action": comp_rec["type"],
                "description": comp_rec["recommendation"],
                "expected_impact": resource_optimization.get(
                    "estimated_savings", {}
                ).get("compression_savings", "70% size reduction"),
            }
        )

    professional_insights = f"""
Professional Performance Optimization Analysis:

Your website's performance analysis reveals several optimization opportunities across multiple areas. The comprehensive audit has identified critical performance bottlenecks and provided a clear roadmap for improvement.

Key focus areas include Core Web Vitals optimization, resource delivery optimization, and advanced performance strategies. The analysis prioritizes fixes by impact versus implementation effort to maximize performance gains.

Implementing these recommendations will significantly improve user experience, reduce bounce rates, and enhance search engine rankings through better Core Web Vitals scores.
"""

    return {
        "ai_powered": False,
        "recommendations": professional_insights,
        "structured_recommendations": recommendations,
        "model_used": "Professional Performance Analysis Algorithm",
    }


def parse_ai_performance_recommendations(recommendations):
    """Parse AI recommendations into structured format"""
    parsed_recommendations = []

    # Basic parsing of AI response into actionable items
    lines = recommendations.split("\n")
    current_category = "General"

    for line in lines:
        line = line.strip()

        # Detect categories
        if any(
            keyword in line.lower() for keyword in ["immediate", "critical", "urgent"]
        ):
            current_category = "Critical Performance"
        elif any(
            keyword in line.lower() for keyword in ["core web vitals", "cwv", "vitals"]
        ):
            current_category = "Core Web Vitals"
        elif any(
            keyword in line.lower() for keyword in ["resource", "assets", "loading"]
        ):
            current_category = "Resource Optimization"
        elif any(keyword in line.lower() for keyword in ["advanced", "long-term"]):
            current_category = "Advanced Optimization"
        elif any(keyword in line.lower() for keyword in ["roadmap", "implementation"]):
            current_category = "Implementation"

        # Extract actionable items
        if line.startswith(("-", "•", "*")) or any(
            action_word in line.lower()
            for action_word in [
                "optimize",
                "implement",
                "enable",
                "reduce",
                "improve",
                "minimize",
            ]
        ):
            priority = (
                "High"
                if current_category in ["Critical Performance", "Core Web Vitals"]
                else "Medium"
            )
            parsed_recommendations.append(
                {
                    "category": current_category,
                    "priority": priority,
                    "action": line.lstrip("-•* "),
                    "description": "AI-recommended performance optimization",
                    "expected_impact": "Performance improvement",
                }
            )

    return parsed_recommendations


def calculate_performance_score(performance_analysis, core_web_vitals):
    """Calculate overall performance score"""
    score_components = {
        "response_time_score": 0,
        "resource_optimization_score": 0,
        "compression_score": 0,
        "caching_score": 0,
        "core_web_vitals_score": 0,
        "overall_score": 0,
    }

    # Response time scoring (25 points)
    response_time = performance_analysis.get("basic_metrics", {}).get(
        "response_time", 999
    )
    if response_time < 0.5:
        score_components["response_time_score"] = 25
    elif response_time < 1.0:
        score_components["response_time_score"] = 20
    elif response_time < 2.0:
        score_components["response_time_score"] = 15
    elif response_time < 3.0:
        score_components["response_time_score"] = 10
    else:
        score_components["response_time_score"] = 5

    # Resource optimization scoring (25 points)
    resource_score = 0
    resource_analysis = performance_analysis.get("resource_analysis", {})
    resource_counts = resource_analysis.get("resource_counts", {})

    # CSS files scoring
    css_files = resource_counts.get("total_css", 0)
    if css_files <= 2:
        resource_score += 8
    elif css_files <= 4:
        resource_score += 6
    elif css_files <= 6:
        resource_score += 4

    # JavaScript optimization scoring
    blocking_js = resource_counts.get("blocking_js", 0)
    if blocking_js == 0:
        resource_score += 8
    elif blocking_js <= 1:
        resource_score += 6
    elif blocking_js <= 2:
        resource_score += 4

    # Image optimization scoring
    image_optimization = performance_analysis.get("image_optimization", {})
    lazy_ratio = image_optimization.get("image_stats", {}).get("lazy_loading_ratio", 0)
    if lazy_ratio >= 80:
        resource_score += 9
    elif lazy_ratio >= 60:
        resource_score += 6
    elif lazy_ratio >= 40:
        resource_score += 3

    score_components["resource_optimization_score"] = resource_score

    # Compression scoring (20 points)
    compression_analysis = performance_analysis.get("compression_analysis", {})
    compression_score = compression_analysis.get("compression_score", 0)
    score_components["compression_score"] = (compression_score / 100) * 20

    # Caching scoring (15 points)
    caching_analysis = performance_analysis.get("caching_analysis", {})
    caching_score = caching_analysis.get("cache_score", 0)
    score_components["caching_score"] = (caching_score / 100) * 15

    # Core Web Vitals scoring (15 points)
    cwv_score = core_web_vitals.get("overall_score", 0)
    score_components["core_web_vitals_score"] = (cwv_score / 100) * 15

    # Calculate overall score
    total_score = sum(score_components.values())
    score_components["overall_score"] = round(total_score, 1)

    # Determine performance grade
    if total_score >= 90:
        grade = "A+"
        performance_level = "Excellent"
    elif total_score >= 80:
        grade = "A"
        performance_level = "Very Good"
    elif total_score >= 70:
        grade = "B"
        performance_level = "Good"
    elif total_score >= 60:
        grade = "C"
        performance_level = "Fair"
    elif total_score >= 50:
        grade = "D"
        performance_level = "Poor"
    else:
        grade = "F"
        performance_level = "Very Poor"

    return {
        "overall_score": total_score,
        "grade": grade,
        "performance_level": performance_level,
        "score_breakdown": score_components,
        "performance_metrics": {
            "response_time": f"{response_time:.2f}s",
            "page_size": f"{performance_analysis.get('basic_metrics', {}).get('total_size', 0) / 1024:.1f}KB",
            "compression_enabled": performance_analysis.get("compression_analysis", {})
            .get("current_compression", {})
            .get("enabled", False),
            "core_web_vitals_rating": f"{cwv_score:.1f}/100",
        },
    }
