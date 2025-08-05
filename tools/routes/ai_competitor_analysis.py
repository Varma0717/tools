from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user
import requests
from urllib.parse import urljoin, urlparse, urlunparse
import re
import time
from datetime import datetime
import json
from bs4 import BeautifulSoup
from utils.professional_decorators import openrouter_api_tool, pro_subscription_required

ai_competitor_analysis_bp = Blueprint("ai_competitor_analysis", __name__)


@ai_competitor_analysis_bp.route("/ai-competitor-analysis")
@openrouter_api_tool
@pro_subscription_required
def ai_competitor_analysis():
    """AI-powered competitor analysis requiring Pro subscription"""
    return render_template("tools/ai_competitor_analysis.html")


@ai_competitor_analysis_bp.route("/ai-competitor-analysis", methods=["POST"])
@openrouter_api_tool
@pro_subscription_required
def ai_competitor_analysis_post():
    """Process AI competitor analysis with comprehensive insights"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        primary_url = data.get("primary_url", "").strip()
        competitor_urls = [
            url.strip() for url in data.get("competitor_urls", []) if url.strip()
        ]

        if not primary_url:
            return jsonify({"error": "Primary website URL is required"}), 400

        if not competitor_urls:
            return jsonify({"error": "At least one competitor URL is required"}), 400

        # Add protocol if missing
        if not primary_url.startswith(("http://", "https://")):
            primary_url = "https://" + primary_url

        competitor_urls = [
            url if url.startswith(("http://", "https://")) else "https://" + url
            for url in competitor_urls
        ]

        # Analyze primary website
        primary_analysis = analyze_website_comprehensive(primary_url, "Primary Website")

        # Analyze competitor websites
        competitor_analyses = []
        for i, comp_url in enumerate(competitor_urls, 1):
            analysis = analyze_website_comprehensive(comp_url, f"Competitor {i}")
            competitor_analyses.append(analysis)

        # Generate competitive analysis
        competitive_insights = generate_competitive_insights(
            primary_analysis, competitor_analyses
        )

        # Generate AI-powered strategic recommendations
        ai_recommendations = generate_ai_competitive_recommendations(
            primary_analysis, competitor_analyses, competitive_insights
        )

        # Generate competitive scoring
        competitive_score = calculate_competitive_position(
            primary_analysis, competitor_analyses
        )

        return jsonify(
            {
                "success": True,
                "primary_url": primary_url,
                "competitor_urls": competitor_urls,
                "primary_analysis": primary_analysis,
                "competitor_analyses": competitor_analyses,
                "competitive_insights": competitive_insights,
                "ai_recommendations": ai_recommendations,
                "competitive_score": competitive_score,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


def analyze_website_comprehensive(url, label="Website"):
    """Perform comprehensive website analysis"""
    analysis = {
        "url": url,
        "label": label,
        "basic_info": {},
        "seo_metrics": {},
        "content_analysis": {},
        "technical_factors": {},
        "social_presence": {},
        "performance_indicators": {},
        "competitive_advantages": [],
    }

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)

        # Basic website information
        analysis["basic_info"] = {
            "status_code": response.status_code,
            "final_url": response.url,
            "response_time": response.elapsed.total_seconds(),
            "server": response.headers.get("server", "Unknown"),
            "content_type": response.headers.get("content-type", ""),
            "content_length": len(response.content),
            "redirects": len(response.history),
        }

        if response.status_code == 200:
            content = response.text
            soup = BeautifulSoup(content, "html.parser")

            # SEO Metrics Analysis
            analysis["seo_metrics"] = analyze_seo_metrics(content, soup)

            # Content Analysis
            analysis["content_analysis"] = analyze_content_strategy(content, soup)

            # Technical Factors
            analysis["technical_factors"] = analyze_technical_implementation(
                content, response, soup
            )

            # Social Presence Indicators
            analysis["social_presence"] = analyze_social_presence(content, soup)

            # Performance Indicators
            analysis["performance_indicators"] = analyze_performance_indicators(
                content, response
            )

            # Identify competitive advantages
            analysis["competitive_advantages"] = identify_competitive_advantages(
                analysis
            )

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


def analyze_seo_metrics(content, soup):
    """Analyze SEO-related metrics"""
    seo_data = {}

    # Title tag analysis
    title_tag = soup.find("title")
    seo_data["title"] = {
        "present": bool(title_tag),
        "content": title_tag.get_text().strip() if title_tag else "",
        "length": len(title_tag.get_text().strip()) if title_tag else 0,
    }

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    seo_data["meta_description"] = {
        "present": bool(meta_desc),
        "content": meta_desc.get("content", "").strip() if meta_desc else "",
        "length": len(meta_desc.get("content", "").strip()) if meta_desc else 0,
    }

    # Heading structure
    headings = {}
    for i in range(1, 7):
        h_tags = soup.find_all(f"h{i}")
        headings[f"h{i}"] = {
            "count": len(h_tags),
            "content": [h.get_text().strip() for h in h_tags[:3]],  # First 3 headings
        }
    seo_data["headings"] = headings

    # Internal and external links
    all_links = soup.find_all("a", href=True)
    internal_links = 0
    external_links = 0

    parsed_url = urlparse(content)
    domain = parsed_url.netloc

    for link in all_links:
        href = link.get("href")
        if href.startswith("http"):
            if domain in href:
                internal_links += 1
            else:
                external_links += 1
        elif href.startswith("/") or not href.startswith(("mailto:", "tel:", "#")):
            internal_links += 1

    seo_data["links"] = {
        "total": len(all_links),
        "internal": internal_links,
        "external": external_links,
    }

    # Image optimization
    images = soup.find_all("img")
    images_with_alt = sum(1 for img in images if img.get("alt"))

    seo_data["images"] = {
        "total": len(images),
        "with_alt": images_with_alt,
        "alt_ratio": (images_with_alt / len(images) * 100) if images else 0,
    }

    # Schema markup detection
    json_ld_scripts = soup.find_all("script", type="application/ld+json")
    microdata_items = soup.find_all(attrs={"itemscope": True})

    seo_data["structured_data"] = {
        "json_ld_count": len(json_ld_scripts),
        "microdata_count": len(microdata_items),
        "has_schema": len(json_ld_scripts) > 0 or len(microdata_items) > 0,
    }

    return seo_data


def analyze_content_strategy(content, soup):
    """Analyze content strategy and quality"""
    content_data = {}

    # Text content analysis
    text_content = soup.get_text()
    words = text_content.split()

    content_data["text_metrics"] = {
        "word_count": len(words),
        "character_count": len(text_content),
        "paragraph_count": len(soup.find_all("p")),
        "list_count": len(soup.find_all(["ul", "ol"])),
    }

    # Content freshness indicators
    date_patterns = re.findall(
        r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b", content
    )
    current_year = str(datetime.now().year)
    recent_dates = [date for date in date_patterns if current_year in date]

    content_data["freshness"] = {
        "date_mentions": len(date_patterns),
        "recent_dates": len(recent_dates),
        "has_blog": "blog" in content.lower() or "news" in content.lower(),
    }

    # Content types
    multimedia_elements = {
        "videos": len(soup.find_all(["video", "iframe"])),
        "images": len(soup.find_all("img")),
        "forms": len(soup.find_all("form")),
        "tables": len(soup.find_all("table")),
    }
    content_data["multimedia"] = multimedia_elements

    # Topic analysis (basic keyword density)
    common_words = {}
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
    }

    for word in words:
        word = re.sub(r"[^\w]", "", word.lower())
        if len(word) > 3 and word not in stop_words:
            common_words[word] = common_words.get(word, 0) + 1

    top_keywords = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:10]
    content_data["top_keywords"] = [
        {"word": word, "count": count} for word, count in top_keywords
    ]

    return content_data


def analyze_technical_implementation(content, response, soup):
    """Analyze technical implementation factors"""
    tech_data = {}

    # Performance factors
    tech_data["performance"] = {
        "page_size": len(content),
        "compression": "gzip" in response.headers.get("content-encoding", ""),
        "cache_control": response.headers.get("cache-control", ""),
        "response_time": response.elapsed.total_seconds(),
    }

    # Security factors
    tech_data["security"] = {
        "https": response.url.startswith("https://"),
        "security_headers": {
            "strict_transport_security": "strict-transport-security"
            in response.headers,
            "x_frame_options": "x-frame-options" in response.headers,
            "x_content_type_options": "x-content-type-options" in response.headers,
            "content_security_policy": "content-security-policy" in response.headers,
        },
    }

    # Mobile optimization
    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    tech_data["mobile"] = {
        "has_viewport": bool(viewport_tag),
        "viewport_content": viewport_tag.get("content", "") if viewport_tag else "",
        "responsive_indicators": "media" in content or "@media" in content,
    }

    # Technology stack detection
    technologies = detect_technologies(content, response)
    tech_data["technologies"] = technologies

    return tech_data


def detect_technologies(content, response):
    """Detect technologies used on the website"""
    tech_stack = {
        "cms": [],
        "frameworks": [],
        "analytics": [],
        "advertising": [],
        "cdn": [],
    }

    content_lower = content.lower()

    # CMS Detection
    cms_indicators = {
        "WordPress": ["wp-content", "wp-includes", "wordpress"],
        "Drupal": ["drupal", "sites/default"],
        "Joomla": ["joomla", "option=com_"],
        "Shopify": ["shopify", "cdn.shopify"],
        "Magento": ["magento", "mage/"],
        "Wix": ["wix.com", "static.wixstatic"],
        "Squarespace": ["squarespace", "static1.squarespace"],
    }

    for cms, indicators in cms_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            tech_stack["cms"].append(cms)

    # Framework Detection
    framework_indicators = {
        "React": ["react", "_react"],
        "Vue.js": ["vue.js", "__vue__"],
        "Angular": ["angular", "ng-"],
        "jQuery": ["jquery", "$."],
        "Bootstrap": ["bootstrap", "btn-"],
        "Foundation": ["foundation", "grid-"],
        "Tailwind CSS": ["tailwindcss", "tw-"],
    }

    for framework, indicators in framework_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            tech_stack["frameworks"].append(framework)

    # Analytics Detection
    analytics_indicators = {
        "Google Analytics": ["google-analytics", "gtag", "ga("],
        "Google Tag Manager": ["googletagmanager", "gtm."],
        "Facebook Pixel": ["facebook.net", "fbevents"],
        "Adobe Analytics": ["adobe", "s_code"],
        "Hotjar": ["hotjar", "hj("],
    }

    for analytics, indicators in analytics_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            tech_stack["analytics"].append(analytics)

    # Advertising Detection
    ad_indicators = {
        "Google Ads": ["googleadservices", "google_ad"],
        "Facebook Ads": ["facebook.com/tr", "fbq("],
        "AdSense": ["googlesyndication", "adsbygoogle"],
        "Amazon Associates": ["amazon-adsystem", "assoc-amazon"],
    }

    for ad_platform, indicators in ad_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            tech_stack["advertising"].append(ad_platform)

    # CDN Detection
    cdn_indicators = {
        "Cloudflare": ["cloudflare", "cf-ray"],
        "AWS CloudFront": ["cloudfront", "aws"],
        "MaxCDN": ["maxcdn", "netdna"],
        "KeyCDN": ["keycdn"],
        "Fastly": ["fastly"],
    }

    for cdn, indicators in cdn_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            tech_stack["cdn"].append(cdn)

    return tech_stack


def analyze_social_presence(content, soup):
    """Analyze social media presence and integration"""
    social_data = {}

    # Social media links
    social_platforms = {
        "facebook": ["facebook.com", "fb.com"],
        "twitter": ["twitter.com", "x.com"],
        "linkedin": ["linkedin.com"],
        "instagram": ["instagram.com"],
        "youtube": ["youtube.com", "youtu.be"],
        "tiktok": ["tiktok.com"],
        "pinterest": ["pinterest.com"],
    }

    found_platforms = {}
    all_links = soup.find_all("a", href=True)

    for platform, domains in social_platforms.items():
        for link in all_links:
            href = link.get("href", "").lower()
            if any(domain in href for domain in domains):
                found_platforms[platform] = href
                break

    social_data["platforms"] = found_platforms

    # Social sharing buttons
    sharing_indicators = ["share", "tweet", "like", "follow", "social"]
    social_buttons = 0

    for indicator in sharing_indicators:
        social_buttons += content.lower().count(indicator)

    social_data["sharing_integration"] = {
        "button_indicators": social_buttons,
        "has_sharing": social_buttons > 3,
    }

    # Open Graph tags
    og_tags = {}
    for meta in soup.find_all("meta"):
        property_val = meta.get("property", "")
        if property_val.startswith("og:"):
            og_tags[property_val] = meta.get("content", "")

    social_data["open_graph"] = og_tags

    # Twitter Card tags
    twitter_tags = {}
    for meta in soup.find_all("meta"):
        name_val = meta.get("name", "")
        if name_val.startswith("twitter:"):
            twitter_tags[name_val] = meta.get("content", "")

    social_data["twitter_cards"] = twitter_tags

    return social_data


def analyze_performance_indicators(content, response):
    """Analyze performance indicators"""
    perf_data = {}

    # Resource loading
    css_count = content.count("<link") + content.count(".css")
    js_count = content.count("<script") + content.count(".js")

    perf_data["resources"] = {
        "css_files": css_count,
        "js_files": js_count,
        "total_requests": css_count + js_count,
    }

    # Caching strategy
    cache_headers = {
        "cache_control": response.headers.get("cache-control", ""),
        "expires": response.headers.get("expires", ""),
        "etag": response.headers.get("etag", ""),
        "last_modified": response.headers.get("last-modified", ""),
    }

    perf_data["caching"] = cache_headers

    # Optimization indicators
    perf_data["optimization"] = {
        "minified_resources": ".min." in content,
        "compression_enabled": "gzip" in response.headers.get("content-encoding", ""),
        "image_optimization": any(
            format in content.lower() for format in ["webp", "avif"]
        ),
        "lazy_loading": 'loading="lazy"' in content,
    }

    return perf_data


def identify_competitive_advantages(analysis):
    """Identify potential competitive advantages"""
    advantages = []

    seo_metrics = analysis.get("seo_metrics", {})
    content_analysis = analysis.get("content_analysis", {})
    technical_factors = analysis.get("technical_factors", {})

    # SEO advantages
    if seo_metrics.get("structured_data", {}).get("has_schema"):
        advantages.append(
            {
                "category": "SEO",
                "advantage": "Schema markup implementation",
                "description": "Uses structured data for better search visibility",
            }
        )

    # Content advantages
    word_count = content_analysis.get("text_metrics", {}).get("word_count", 0)
    if word_count > 2000:
        advantages.append(
            {
                "category": "Content",
                "advantage": "Comprehensive content",
                "description": f"Rich content with {word_count} words",
            }
        )

    # Technical advantages
    if technical_factors.get("security", {}).get("https"):
        advantages.append(
            {
                "category": "Security",
                "advantage": "HTTPS encryption",
                "description": "Secure connection with SSL/TLS",
            }
        )

    # Performance advantages
    response_time = analysis.get("basic_info", {}).get("response_time", 999)
    if response_time < 1.0:
        advantages.append(
            {
                "category": "Performance",
                "advantage": "Fast loading speed",
                "description": f"Quick response time of {response_time:.2f}s",
            }
        )

    return advantages


def generate_competitive_insights(primary_analysis, competitor_analyses):
    """Generate competitive insights by comparing websites"""
    insights = {
        "content_comparison": {},
        "seo_comparison": {},
        "technical_comparison": {},
        "performance_comparison": {},
        "gaps_and_opportunities": [],
    }

    # Content comparison
    primary_words = (
        primary_analysis.get("content_analysis", {})
        .get("text_metrics", {})
        .get("word_count", 0)
    )
    competitor_words = [
        comp.get("content_analysis", {}).get("text_metrics", {}).get("word_count", 0)
        for comp in competitor_analyses
    ]
    avg_competitor_words = (
        sum(competitor_words) / len(competitor_words) if competitor_words else 0
    )

    insights["content_comparison"] = {
        "primary_word_count": primary_words,
        "competitor_avg_words": avg_competitor_words,
        "content_length_position": (
            "Above average" if primary_words > avg_competitor_words else "Below average"
        ),
    }

    # SEO comparison
    primary_schema = (
        primary_analysis.get("seo_metrics", {})
        .get("structured_data", {})
        .get("has_schema", False)
    )
    competitor_schema_count = sum(
        1
        for comp in competitor_analyses
        if comp.get("seo_metrics", {})
        .get("structured_data", {})
        .get("has_schema", False)
    )

    insights["seo_comparison"] = {
        "primary_has_schema": primary_schema,
        "competitors_with_schema": competitor_schema_count,
        "schema_advantage": primary_schema
        and competitor_schema_count < len(competitor_analyses) / 2,
    }

    # Technical comparison
    primary_https = (
        primary_analysis.get("technical_factors", {})
        .get("security", {})
        .get("https", False)
    )
    competitor_https_count = sum(
        1
        for comp in competitor_analyses
        if comp.get("technical_factors", {}).get("security", {}).get("https", False)
    )

    insights["technical_comparison"] = {
        "primary_https": primary_https,
        "competitors_with_https": competitor_https_count,
        "security_position": (
            "Leading"
            if primary_https and competitor_https_count < len(competitor_analyses)
            else "Following"
        ),
    }

    # Performance comparison
    primary_response_time = primary_analysis.get("basic_info", {}).get(
        "response_time", 999
    )
    competitor_response_times = [
        comp.get("basic_info", {}).get("response_time", 999)
        for comp in competitor_analyses
    ]
    avg_competitor_response_time = (
        sum(competitor_response_times) / len(competitor_response_times)
        if competitor_response_times
        else 999
    )

    insights["performance_comparison"] = {
        "primary_response_time": primary_response_time,
        "competitor_avg_response_time": avg_competitor_response_time,
        "performance_position": (
            "Faster"
            if primary_response_time < avg_competitor_response_time
            else "Slower"
        ),
    }

    # Identify gaps and opportunities
    gaps = []

    # Content gaps
    if primary_words < avg_competitor_words * 0.8:
        gaps.append(
            {
                "type": "Content Gap",
                "description": "Content is significantly shorter than competitors",
                "opportunity": "Expand content with more comprehensive information",
            }
        )

    # SEO gaps
    if not primary_schema and competitor_schema_count > 0:
        gaps.append(
            {
                "type": "SEO Gap",
                "description": "Missing structured data implementation",
                "opportunity": "Implement schema markup for better search visibility",
            }
        )

    # Technical gaps
    if not primary_https:
        gaps.append(
            {
                "type": "Security Gap",
                "description": "Website not using HTTPS",
                "opportunity": "Migrate to HTTPS for security and SEO benefits",
            }
        )

    # Performance gaps
    if primary_response_time > avg_competitor_response_time * 1.5:
        gaps.append(
            {
                "type": "Performance Gap",
                "description": "Slower loading speed than competitors",
                "opportunity": "Optimize website performance for better user experience",
            }
        )

    insights["gaps_and_opportunities"] = gaps

    return insights


def generate_ai_competitive_recommendations(
    primary_analysis, competitor_analyses, competitive_insights
):
    """Generate AI-powered competitive recommendations"""
    try:
        import os
        import requests

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return generate_fallback_competitive_recommendations(competitive_insights)

        # Prepare competitive analysis summary for AI
        primary_url = primary_analysis.get("url", "Your website")
        competitor_urls = [
            comp.get("url", "Competitor") for comp in competitor_analyses
        ]

        content_comparison = competitive_insights.get("content_comparison", {})
        seo_comparison = competitive_insights.get("seo_comparison", {})
        technical_comparison = competitive_insights.get("technical_comparison", {})
        performance_comparison = competitive_insights.get("performance_comparison", {})
        gaps = competitive_insights.get("gaps_and_opportunities", [])

        analysis_summary = f"""
        Competitive Analysis Summary:
        
        Primary Website: {primary_url}
        Competitors: {', '.join(competitor_urls)}
        
        Content Analysis:
        - Your content: {content_comparison.get('primary_word_count', 0)} words
        - Competitor average: {content_comparison.get('competitor_avg_words', 0):.0f} words
        - Position: {content_comparison.get('content_length_position', 'Unknown')}
        
        SEO Comparison:
        - Your schema markup: {'Yes' if seo_comparison.get('primary_has_schema') else 'No'}
        - Competitors with schema: {seo_comparison.get('competitors_with_schema', 0)}/{len(competitor_analyses)}
        
        Technical Comparison:
        - Your HTTPS: {'Yes' if technical_comparison.get('primary_https') else 'No'}
        - Competitors with HTTPS: {technical_comparison.get('competitors_with_https', 0)}/{len(competitor_analyses)}
        - Security position: {technical_comparison.get('security_position', 'Unknown')}
        
        Performance:
        - Your response time: {performance_comparison.get('primary_response_time', 0):.2f}s
        - Competitor average: {performance_comparison.get('competitor_avg_response_time', 0):.2f}s
        - Performance position: {performance_comparison.get('performance_position', 'Unknown')}
        
        Identified Gaps: {len(gaps)} opportunities found
        """

        prompt = f"""As a competitive strategy expert, analyze this website comparison and provide actionable recommendations:

{analysis_summary}

Please provide specific, actionable recommendations in these areas:

1. **Content Strategy**: How to improve content to outperform competitors
2. **SEO Optimization**: Technical and on-page SEO improvements to gain competitive advantage
3. **Performance Enhancement**: Speed and technical optimizations to surpass competitors
4. **Competitive Differentiation**: Unique opportunities to stand out from competitors
5. **Quick Wins**: Immediate actions that can provide competitive advantages

Focus on practical, implementable strategies that address the identified gaps and leverage competitive opportunities."""

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
                "strategic_insights": parse_ai_competitive_recommendations(
                    recommendations
                ),
                "model_used": "meta-llama/llama-3.1-8b-instruct",
            }

    except Exception as e:
        print(f"AI analysis error: {e}")

    return generate_fallback_competitive_recommendations(competitive_insights)


def generate_fallback_competitive_recommendations(competitive_insights):
    """Generate fallback recommendations when AI is unavailable"""
    recommendations = []

    gaps = competitive_insights.get("gaps_and_opportunities", [])
    content_comparison = competitive_insights.get("content_comparison", {})
    seo_comparison = competitive_insights.get("seo_comparison", {})
    performance_comparison = competitive_insights.get("performance_comparison", {})

    # Content recommendations
    if content_comparison.get("content_length_position") == "Below average":
        recommendations.append(
            {
                "category": "Content Strategy",
                "priority": "High",
                "action": "Expand content depth and breadth",
                "description": f"Your content ({content_comparison.get('primary_word_count', 0)} words) is below competitor average. Add comprehensive guides, FAQs, and detailed explanations.",
            }
        )

    # SEO recommendations
    if (
        not seo_comparison.get("primary_has_schema")
        and seo_comparison.get("competitors_with_schema", 0) > 0
    ):
        recommendations.append(
            {
                "category": "SEO Optimization",
                "priority": "High",
                "action": "Implement structured data markup",
                "description": "Add schema markup to match competitor SEO advantages and improve search visibility.",
            }
        )

    # Performance recommendations
    if performance_comparison.get("performance_position") == "Slower":
        recommendations.append(
            {
                "category": "Performance",
                "priority": "High",
                "action": "Optimize website speed",
                "description": f"Your response time ({performance_comparison.get('primary_response_time', 0):.2f}s) is slower than competitors. Optimize images, enable compression, and improve caching.",
            }
        )

    # Add specific gap-based recommendations
    for gap in gaps:
        recommendations.append(
            {
                "category": gap.get("type", "General").replace(" Gap", ""),
                "priority": "Medium",
                "action": gap.get("opportunity", ""),
                "description": gap.get("description", ""),
            }
        )

    strategic_insights = f"""
Professional Competitive Analysis Insights:

Based on the comprehensive analysis of your website against {len(competitive_insights.get('content_comparison', {}))} competitors, several strategic opportunities have been identified.

Your competitive position shows areas for improvement in content depth, technical implementation, and performance optimization. The analysis reveals specific gaps that, when addressed, can significantly improve your competitive standing.

Key focus areas include content expansion, technical SEO enhancements, and performance optimizations that will help you surpass competitor benchmarks and establish market leadership.
"""

    return {
        "ai_powered": False,
        "recommendations": strategic_insights,
        "strategic_insights": recommendations,
        "model_used": "Professional Competitive Analysis Algorithm",
    }


def parse_ai_competitive_recommendations(recommendations):
    """Parse AI recommendations into structured format"""
    parsed_recommendations = []

    # Basic parsing of AI response into actionable items
    lines = recommendations.split("\n")
    current_category = "General"

    for line in lines:
        line = line.strip()

        # Detect categories
        if any(keyword in line.lower() for keyword in ["content strategy", "content"]):
            current_category = "Content Strategy"
        elif any(
            keyword in line.lower() for keyword in ["seo", "search", "optimization"]
        ):
            current_category = "SEO Optimization"
        elif any(keyword in line.lower() for keyword in ["performance", "speed"]):
            current_category = "Performance"
        elif any(
            keyword in line.lower() for keyword in ["competitive", "differentiation"]
        ):
            current_category = "Competitive Strategy"
        elif any(keyword in line.lower() for keyword in ["quick wins", "immediate"]):
            current_category = "Quick Wins"

        # Extract actionable items
        if line.startswith(("-", "•", "*")) or any(
            action_word in line.lower()
            for action_word in [
                "implement",
                "add",
                "optimize",
                "improve",
                "create",
                "develop",
            ]
        ):
            parsed_recommendations.append(
                {
                    "category": current_category,
                    "priority": (
                        "High" if "quick win" in current_category.lower() else "Medium"
                    ),
                    "action": line.lstrip("-•* "),
                    "description": "AI-recommended competitive strategy",
                }
            )

    return parsed_recommendations


def calculate_competitive_position(primary_analysis, competitor_analyses):
    """Calculate competitive position score"""
    score_factors = {
        "content_score": 0,
        "seo_score": 0,
        "technical_score": 0,
        "performance_score": 0,
        "overall_score": 0,
    }

    # Content scoring
    primary_words = (
        primary_analysis.get("content_analysis", {})
        .get("text_metrics", {})
        .get("word_count", 0)
    )
    competitor_words = [
        comp.get("content_analysis", {}).get("text_metrics", {}).get("word_count", 0)
        for comp in competitor_analyses
    ]
    avg_competitor_words = (
        sum(competitor_words) / len(competitor_words) if competitor_words else 1
    )

    content_ratio = (
        primary_words / avg_competitor_words if avg_competitor_words > 0 else 1
    )
    score_factors["content_score"] = min(100, content_ratio * 50 + 50)  # Scale to 0-100

    # SEO scoring
    seo_score = 0
    primary_seo = primary_analysis.get("seo_metrics", {})

    if primary_seo.get("title", {}).get("present"):
        seo_score += 25
    if primary_seo.get("meta_description", {}).get("present"):
        seo_score += 25
    if primary_seo.get("structured_data", {}).get("has_schema"):
        seo_score += 25
    if primary_seo.get("headings", {}).get("h1", {}).get("count", 0) == 1:
        seo_score += 25

    score_factors["seo_score"] = seo_score

    # Technical scoring
    technical_score = 0
    primary_tech = primary_analysis.get("technical_factors", {})

    if primary_tech.get("security", {}).get("https"):
        technical_score += 30
    if primary_tech.get("mobile", {}).get("has_viewport"):
        technical_score += 30
    if primary_tech.get("performance", {}).get("compression"):
        technical_score += 20
    if len(primary_tech.get("technologies", {}).get("frameworks", [])) > 0:
        technical_score += 20

    score_factors["technical_score"] = technical_score

    # Performance scoring
    primary_response_time = primary_analysis.get("basic_info", {}).get(
        "response_time", 999
    )
    competitor_response_times = [
        comp.get("basic_info", {}).get("response_time", 999)
        for comp in competitor_analyses
    ]
    avg_competitor_response_time = (
        sum(competitor_response_times) / len(competitor_response_times)
        if competitor_response_times
        else 999
    )

    if primary_response_time < 1.0:
        performance_score = 100
    elif primary_response_time < 2.0:
        performance_score = 80
    elif primary_response_time < 3.0:
        performance_score = 60
    elif primary_response_time < 5.0:
        performance_score = 40
    else:
        performance_score = 20

    # Bonus for being faster than competitors
    if primary_response_time < avg_competitor_response_time:
        performance_score = min(100, performance_score + 20)

    score_factors["performance_score"] = performance_score

    # Overall score calculation
    weights = {
        "content_score": 0.3,
        "seo_score": 0.3,
        "technical_score": 0.25,
        "performance_score": 0.15,
    }

    overall_score = sum(
        score_factors[factor] * weight for factor, weight in weights.items()
    )
    score_factors["overall_score"] = round(overall_score, 1)

    # Determine competitive position
    if overall_score >= 85:
        position = "Market Leader"
        position_description = "Your website significantly outperforms competitors"
    elif overall_score >= 70:
        position = "Strong Competitor"
        position_description = "Your website performs well against competition"
    elif overall_score >= 55:
        position = "Average Performer"
        position_description = (
            "Your website is competitive but has room for improvement"
        )
    elif overall_score >= 40:
        position = "Below Average"
        position_description = "Your website underperforms compared to competitors"
    else:
        position = "Needs Improvement"
        position_description = "Significant optimization needed to compete effectively"

    return {
        "overall_score": overall_score,
        "position": position,
        "position_description": position_description,
        "score_breakdown": score_factors,
        "ranking_factors": {
            "content_performance": (
                "Above average"
                if score_factors["content_score"] > 75
                else "Below average"
            ),
            "seo_performance": (
                "Strong" if score_factors["seo_score"] > 75 else "Needs improvement"
            ),
            "technical_performance": (
                "Advanced" if score_factors["technical_score"] > 75 else "Basic"
            ),
            "speed_performance": (
                "Fast" if score_factors["performance_score"] > 75 else "Slow"
            ),
        },
    }
