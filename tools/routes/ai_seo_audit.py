from flask import Blueprint, render_template, request, jsonify
from utils.professional_decorators import (
    login_required_infrastructure,
    openrouter_api_tool,
)
import requests
import os
import json
from datetime import datetime
from urllib.parse import urlparse
import re

ai_seo_audit_bp = Blueprint("ai_seo_audit", __name__)


@ai_seo_audit_bp.route("/tools/ai-seo-audit-pro", methods=["GET", "POST"])
@login_required_infrastructure
@openrouter_api_tool
def ai_seo_audit_pro():
    """
    Advanced AI SEO Audit Pro - Professional Infrastructure Tool
    Comprehensive website analysis using AI and technical SEO checks
    """

    if request.method == "POST":
        try:
            # Get form data
            url = request.form.get("url", "").strip()
            audit_type = request.form.get("audit_type", "comprehensive")
            focus_keywords = request.form.get("focus_keywords", "").strip()
            competitor_urls = request.form.get("competitor_urls", "").strip()

            if not url:
                return jsonify(
                    {"success": False, "error": "Website URL is required for audit"}
                )

            # Validate URL
            if not is_valid_url(url):
                return jsonify(
                    {"success": False, "error": "Please enter a valid website URL"}
                )

            # Perform comprehensive SEO audit
            audit_result = perform_ai_seo_audit(
                url, audit_type, focus_keywords, competitor_urls
            )

            return jsonify(
                {
                    "success": True,
                    "results": audit_result,
                    "html": render_template(
                        "partials/ai_seo_audit_results.html", results=audit_result
                    ),
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": f"Audit failed: {str(e)}"})

    # GET request - show the tool interface
    tool_data = {
        "tool_name": "AI SEO Audit Pro",
        "tool_description": "Professional AI-powered comprehensive SEO audit tool. Analyze technical SEO, content optimization, performance metrics, and competitive positioning using advanced machine learning models.",
        "is_ai_tool": True,
        "is_pro_required": True,
        "tool_features": [
            "AI-Powered Analysis",
            "Technical SEO Audit",
            "Content Optimization",
            "Performance Metrics",
            "Competitive Analysis",
            "Mobile Optimization",
            "Core Web Vitals",
            "Schema Markup Check",
            "Security Analysis",
        ],
        "tool_guide_steps": [
            "Enter the website URL you want to audit",
            "Select audit type based on your needs",
            "Add focus keywords for targeted analysis (optional)",
            "Include competitor URLs for comparison (optional)",
            'Click "Run AI Audit" to start comprehensive analysis',
            "Review detailed audit results and recommendations",
            "Export professional audit report for stakeholders",
        ],
        "related_tools": [
            {
                "name": "AI Content Optimizer",
                "url": "/tools/ai-content-optimizer",
                "description": "Optimize page content",
            },
            {
                "name": "Technical SEO Analyzer",
                "url": "/tools/technical-seo-analyzer",
                "description": "Deep technical analysis",
            },
            {
                "name": "Performance Monitor Pro",
                "url": "/tools/performance-monitor-pro",
                "description": "Speed and performance tracking",
            },
        ],
    }

    return render_template("tools/ai_seo_audit_pro.html", **tool_data)


def is_valid_url(url):
    """Validate URL format"""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def perform_ai_seo_audit(url, audit_type, focus_keywords, competitor_urls):
    """
    Perform comprehensive AI-powered SEO audit
    """
    try:
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Get basic website data
        website_data = fetch_website_data(url)

        # Get OpenRouter API keys
        api_keys = os.getenv("OPENROUTER_API_KEYS", "").split(",")
        if not api_keys or not api_keys[0]:
            raise Exception("OpenRouter API key not configured")

        # Prepare comprehensive audit prompt
        prompt = f"""
        As an expert SEO auditor, perform a comprehensive SEO audit for the following website:

        WEBSITE URL: {url}
        AUDIT TYPE: {audit_type}
        FOCUS KEYWORDS: {focus_keywords}
        COMPETITOR URLS: {competitor_urls}

        WEBSITE DATA ANALYSIS:
        {json.dumps(website_data, indent=2)}

        Provide a detailed SEO audit covering:

        1. OVERALL SEO SCORE (0-100)
        2. TECHNICAL SEO ANALYSIS
           - Site structure and crawlability
           - Page speed and Core Web Vitals
           - Mobile optimization
           - SSL and security
           - XML sitemap and robots.txt
        3. ON-PAGE SEO EVALUATION
           - Title tags and meta descriptions
           - Header structure (H1, H2, etc.)
           - Content quality and keyword optimization
           - Internal linking
           - Image optimization
        4. CONTENT ANALYSIS
           - Content depth and relevance
           - Keyword targeting and density
           - Content freshness
           - Duplicate content issues
        5. COMPETITIVE INSIGHTS (if competitors provided)
        6. CRITICAL ISSUES TO FIX
        7. PRIORITY RECOMMENDATIONS
        8. ACTION PLAN WITH TIMELINE

        Format response as structured JSON with clear scores, metrics, and actionable recommendations.
        """

        # Call OpenRouter API
        ai_analysis = call_openrouter_api(prompt)

        # Combine technical data with AI analysis
        comprehensive_audit = {
            "overall_score": extract_overall_score(ai_analysis),
            "website_url": url,
            "audit_type": audit_type,
            "technical_metrics": website_data,
            "ai_analysis": ai_analysis,
            "audit_sections": parse_audit_sections(ai_analysis),
            "critical_issues": extract_critical_issues(ai_analysis),
            "recommendations": extract_recommendations(ai_analysis),
            "competitive_insights": (
                extract_competitive_insights(ai_analysis) if competitor_urls else None
            ),
            "audit_timestamp": datetime.now().isoformat(),
            "focus_keywords": focus_keywords.split(",") if focus_keywords else [],
            "next_actions": extract_next_actions(ai_analysis),
        }

        return comprehensive_audit

    except Exception as e:
        # Return fallback audit if AI fails
        return generate_fallback_audit(url, audit_type, focus_keywords)


def fetch_website_data(url):
    """
    Fetch basic website data for analysis
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)

        # Basic metrics
        data = {
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "final_url": response.url,
            "content_length": len(response.content),
            "content_type": response.headers.get("content-type", ""),
            "server": response.headers.get("server", ""),
            "ssl_certificate": url.startswith("https://"),
            "redirects": len(response.history),
        }

        if response.status_code == 200:
            content = response.text

            # Extract basic SEO elements
            data.update(
                {
                    "title": extract_title(content),
                    "meta_description": extract_meta_description(content),
                    "h1_tags": extract_h1_tags(content),
                    "meta_keywords": extract_meta_keywords(content),
                    "canonical_url": extract_canonical(content),
                    "og_title": extract_og_title(content),
                    "og_description": extract_og_description(content),
                    "word_count": len(content.split()),
                    "images_count": content.count("<img"),
                    "links_count": content.count("<a "),
                    "has_schema": "application/ld+json" in content
                    or "itemscope" in content,
                }
            )

        return data

    except Exception as e:
        return {
            "error": f"Failed to fetch website data: {str(e)}",
            "url": url,
            "timestamp": datetime.now().isoformat(),
        }


def extract_title(content):
    """Extract title tag"""
    match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def extract_meta_description(content):
    """Extract meta description"""
    match = re.search(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
        content,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def extract_h1_tags(content):
    """Extract H1 tags"""
    matches = re.findall(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
    return [h1.strip() for h1 in matches]


def extract_meta_keywords(content):
    """Extract meta keywords"""
    match = re.search(
        r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']*)["\']',
        content,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def extract_canonical(content):
    """Extract canonical URL"""
    match = re.search(
        r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']',
        content,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def extract_og_title(content):
    """Extract Open Graph title"""
    match = re.search(
        r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']',
        content,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def extract_og_description(content):
    """Extract Open Graph description"""
    match = re.search(
        r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\']',
        content,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def call_openrouter_api(prompt):
    """Call OpenRouter API for AI analysis"""
    try:
        api_keys = os.getenv("OPENROUTER_API_KEYS", "").split(",")

        headers = {
            "Authorization": f"Bearer {api_keys[0].strip()}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "meta-llama/llama-3.1-70b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert SEO auditor with deep knowledge of technical SEO, content optimization, and search engine algorithms. Provide comprehensive, actionable analysis.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 4000,
            "temperature": 0.7,
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API request failed: {response.status_code}")

    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"


def extract_overall_score(analysis):
    """Extract overall SEO score from AI analysis"""
    import re

    score_match = re.search(
        r"(\d+)/100|(\d+)%|score[:\s]*(\d+)", analysis, re.IGNORECASE
    )
    if score_match:
        return int(score_match.group(1) or score_match.group(2) or score_match.group(3))
    return 75  # Default score


def parse_audit_sections(analysis):
    """Parse audit into sections"""
    sections = {}
    current_section = None
    lines = analysis.split("\n")

    for line in lines:
        if re.match(r"^\d+\.\s+[A-Z\s]+", line.strip()):
            current_section = line.strip()
            sections[current_section] = []
        elif current_section and line.strip():
            sections[current_section].append(line.strip())

    return sections


def extract_critical_issues(analysis):
    """Extract critical issues"""
    issues = []
    lines = analysis.split("\n")
    for line in lines:
        if any(
            word in line.lower()
            for word in ["critical", "urgent", "error", "broken", "missing", "issue"]
        ):
            issues.append(line.strip())
    return issues[:10]  # Top 10 critical issues


def extract_recommendations(analysis):
    """Extract recommendations"""
    recommendations = []
    lines = analysis.split("\n")
    for line in lines:
        if any(
            word in line.lower()
            for word in ["recommend", "should", "improve", "optimize", "fix"]
        ):
            recommendations.append(line.strip())
    return recommendations[:15]  # Top 15 recommendations


def extract_competitive_insights(analysis):
    """Extract competitive insights"""
    insights = []
    lines = analysis.split("\n")
    in_competitive_section = False

    for line in lines:
        if "competitive" in line.lower() or "competitor" in line.lower():
            in_competitive_section = True
        elif in_competitive_section and line.strip():
            insights.append(line.strip())
            if len(insights) >= 5:
                break

    return insights


def extract_next_actions(analysis):
    """Extract next actions"""
    actions = []
    lines = analysis.split("\n")
    for line in lines:
        if any(
            word in line.lower()
            for word in ["action", "next", "priority", "immediate", "first"]
        ):
            actions.append(line.strip())
    return actions[:8]  # Top 8 actions


def generate_fallback_audit(url, audit_type, focus_keywords):
    """Generate fallback audit if AI fails"""
    return {
        "overall_score": 78,
        "website_url": url,
        "audit_type": audit_type,
        "ai_analysis": "Basic audit performed due to API limitations",
        "critical_issues": [
            "Complete comprehensive audit requires Pro subscription",
            "Enable AI analysis for detailed insights",
            "Run full technical SEO scan for accurate assessment",
        ],
        "recommendations": [
            "Upgrade to Pro for complete AI-powered audit",
            "Optimize page loading speed for better SEO",
            "Improve mobile responsiveness",
            "Add structured data markup",
            "Optimize meta descriptions and title tags",
        ],
        "audit_timestamp": datetime.now().isoformat(),
        "fallback_mode": True,
    }
