from flask import Blueprint, render_template, request, jsonify
from utils.professional_decorators import login_required_infrastructure
from bs4 import BeautifulSoup
import requests
from datetime import datetime

meta_tag_analyzer_bp = Blueprint("meta_tag_analyzer", __name__, url_prefix="/tools")

IMPORTANT_TAGS = [
    "title",
    "description",
    "keywords",
    "robots",
    "canonical",
    "og:title",
    "og:description",
    "og:image",
    "og:type",
    "og:url",
    "og:site_name",
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
    "viewport",
    "charset",
    "author",
    "generator",
    "rating",
]


def get_tag_score(tag, value):
    """Professional scoring algorithm for meta tags"""
    if not value:
        return {
            "score": 0,
            "status": "missing",
            "recommendation": f"{tag} tag is missing",
        }

    score = 0
    status = "good"
    recommendation = f"{tag} tag is properly configured"

    if tag in ["title", "og:title", "twitter:title"]:
        length = len(value)
        if 50 <= length <= 60:
            score = 100
        elif 30 <= length <= 70:
            score = 80
        elif length < 30:
            score = 40
            status = "warning"
            recommendation = f"{tag} is too short (recommended: 50-60 characters)"
        else:
            score = 60
            status = "warning"
            recommendation = f"{tag} is too long (recommended: 50-60 characters)"

    elif tag in ["description", "og:description", "twitter:description"]:
        length = len(value)
        if 150 <= length <= 160:
            score = 100
        elif 120 <= length <= 180:
            score = 80
        elif length < 120:
            score = 50
            status = "warning"
            recommendation = f"{tag} is too short (recommended: 150-160 characters)"
        else:
            score = 60
            status = "warning"
            recommendation = f"{tag} is too long (recommended: 150-160 characters)"

    elif tag == "canonical":
        if value.startswith(("http://", "https://")):
            score = 100
        else:
            score = 40
            status = "error"
            recommendation = "Canonical URL should be absolute"

    elif tag == "robots":
        if any(directive in value.lower() for directive in ["index", "follow"]):
            score = 100
        elif "noindex" in value.lower():
            score = 80
            status = "warning"
            recommendation = "Page is set to noindex"
        else:
            score = 60

    else:
        score = 90 if value else 0

    return {
        "score": score,
        "status": status,
        "recommendation": recommendation,
        "length": len(value) if value else 0,
    }


@meta_tag_analyzer_bp.route(
    "/meta-tag-analyzer", methods=["GET", "POST"], endpoint="meta_tag_analyzer"
)
@login_required_infrastructure
def meta_tag_analyzer():
    """
    Professional Meta Tag Analyzer - Infrastructure Tool
    Requires authentication for access
    """

    if request.method == "POST":
        try:
            url = request.form.get("url", "").strip()

            if not url:
                return jsonify(
                    {"success": False, "error": "URL is required for analysis"}
                )

            # Ensure URL has protocol
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # Analyze meta tags
            analysis_result = analyze_meta_tags(url)

            return jsonify(
                {
                    "success": True,
                    "results": analysis_result,
                    "html": render_template(
                        "partials/meta_tag_results.html", results=analysis_result
                    ),
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"})

    # GET request - show the tool interface
    tool_data = {
        "tool_name": "Advanced Meta Tag Analyzer",
        "tool_description": "Professional meta tag analysis tool for developers and SEO specialists. Comprehensive scoring, optimization recommendations, and detailed technical insights.",
        "is_ai_tool": False,
        "is_pro_required": False,
        "tool_features": [
            "Comprehensive Tag Analysis",
            "Professional Scoring System",
            "Optimization Recommendations",
            "Social Media Preview",
            "Technical SEO Insights",
            "Competitor Comparison",
            "Export Reports",
        ],
        "tool_guide_steps": [
            "Enter the website URL you want to analyze",
            'Click "Run Analysis" to fetch and analyze meta tags',
            "Review comprehensive scoring and recommendations",
            "Check social media preview optimization",
            "Identify missing or problematic tags",
            "Export detailed analysis report",
            "Implement recommended optimizations",
        ],
        "related_tools": [
            {
                "name": "Open Graph Preview",
                "url": "/tools/open-graph-preview",
                "description": "Preview social sharing",
            },
            {
                "name": "SERP Snippet Preview",
                "url": "/tools/serp-snippet-preview",
                "description": "Preview search results",
            },
            {
                "name": "AI SEO Audit Pro",
                "url": "/tools/ai-seo-audit-pro",
                "description": "Complete AI audit",
            },
        ],
    }

    return render_template("tools/meta_tag_analyzer.html", **tool_data)


def analyze_meta_tags(url):
    """
    Perform comprehensive meta tag analysis
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all meta tags
        all_tags = []
        scores = {}

        # Title tag
        title = soup.title.string.strip() if soup.title else ""
        if title:
            all_tags.append({"name": "title", "value": title})

        # Meta tags
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property") or tag.get("http-equiv")
            content = tag.get("content") or tag.get("value") or ""
            charset = tag.get("charset")

            if name and content:
                all_tags.append({"name": name, "value": content})
            elif charset:
                all_tags.append({"name": "charset", "value": charset})

        # Canonical link
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            all_tags.append({"name": "canonical", "value": canonical.get("href")})

        # Other important links
        for link in soup.find_all("link"):
            rel = link.get("rel")
            if rel and link.get("href"):
                rel = " ".join(rel) if isinstance(rel, list) else rel
                if rel in ["alternate", "amphtml", "prev", "next"]:
                    all_tags.append({"name": f"link:{rel}", "value": link.get("href")})

        # Score important tags
        found_tags = {tag["name"]: tag["value"] for tag in all_tags}

        for important_tag in IMPORTANT_TAGS:
            value = found_tags.get(important_tag, "")
            scores[important_tag] = get_tag_score(important_tag, value)

        # Calculate overall score
        total_score = sum(score["score"] for score in scores.values())
        max_possible = len(IMPORTANT_TAGS) * 100
        overall_score = (
            int((total_score / max_possible) * 100) if max_possible > 0 else 0
        )

        # Generate insights
        insights = generate_meta_tag_insights(scores, found_tags)

        return {
            "url": url,
            "overall_score": overall_score,
            "all_tags": all_tags,
            "scores": scores,
            "insights": insights,
            "analysis_timestamp": datetime.now().isoformat(),
            "total_tags_found": len(all_tags),
            "important_tags_found": len(
                [tag for tag in IMPORTANT_TAGS if found_tags.get(tag)]
            ),
            "social_media_optimized": check_social_optimization(found_tags),
            "seo_readiness": calculate_seo_readiness(scores),
        }

    except Exception as e:
        raise Exception(f"Failed to analyze meta tags: {str(e)}")


def generate_meta_tag_insights(scores, found_tags):
    """Generate professional insights and recommendations"""
    insights = {
        "critical_issues": [],
        "warnings": [],
        "recommendations": [],
        "good_practices": [],
    }

    for tag, score_data in scores.items():
        if score_data["status"] == "missing":
            insights["critical_issues"].append(
                f"Missing {tag} tag - this is critical for SEO"
            )
        elif score_data["status"] == "error":
            insights["critical_issues"].append(f"{tag}: {score_data['recommendation']}")
        elif score_data["status"] == "warning":
            insights["warnings"].append(f"{tag}: {score_data['recommendation']}")
        elif score_data["score"] >= 90:
            insights["good_practices"].append(f"{tag} is well optimized")

    # Additional recommendations
    if not found_tags.get("og:image"):
        insights["recommendations"].append(
            "Add Open Graph image for better social media sharing"
        )

    if not found_tags.get("twitter:card"):
        insights["recommendations"].append(
            "Add Twitter Card markup for Twitter optimization"
        )

    if found_tags.get("description") and len(found_tags["description"]) > 160:
        insights["recommendations"].append(
            "Meta description is too long for optimal display"
        )

    return insights


def check_social_optimization(found_tags):
    """Check if page is optimized for social media"""
    required_og = ["og:title", "og:description", "og:image", "og:url"]
    required_twitter = ["twitter:card", "twitter:title", "twitter:description"]

    og_score = sum(1 for tag in required_og if found_tags.get(tag))
    twitter_score = sum(1 for tag in required_twitter if found_tags.get(tag))

    return {
        "facebook_ready": og_score >= 3,
        "twitter_ready": twitter_score >= 2,
        "overall_social_score": int(((og_score + twitter_score) / 7) * 100),
    }


def calculate_seo_readiness(scores):
    """Calculate SEO readiness percentage"""
    critical_tags = ["title", "description", "canonical"]
    critical_scores = [scores.get(tag, {"score": 0})["score"] for tag in critical_tags]

    if not critical_scores:
        return 0

    return int(sum(critical_scores) / len(critical_scores))
