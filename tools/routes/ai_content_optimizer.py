from flask import Blueprint, render_template, request, jsonify, flash
from utils.professional_decorators import (
    login_required_infrastructure,
    openrouter_api_tool,
)
import requests
import os
import json
from datetime import datetime

ai_content_optimizer_bp = Blueprint("ai_content_optimizer", __name__)


@ai_content_optimizer_bp.route("/tools/ai-content-optimizer", methods=["GET", "POST"])
@login_required_infrastructure
@openrouter_api_tool
def ai_content_optimizer():
    """
    Advanced AI Content Optimizer - Professional Infrastructure Tool
    Uses OpenRouter API for comprehensive content analysis and optimization
    """

    if request.method == "POST":
        try:
            # Get form data
            content = request.form.get("content", "").strip()
            target_keywords = request.form.get("target_keywords", "").strip()
            content_type = request.form.get("content_type", "blog_post")
            optimization_level = request.form.get("optimization_level", "standard")

            if not content:
                return jsonify(
                    {"success": False, "error": "Content is required for optimization"}
                )

            # Call OpenRouter API for content optimization
            result = optimize_content_with_ai(
                content, target_keywords, content_type, optimization_level
            )

            return jsonify(
                {
                    "success": True,
                    "results": result,
                    "html": render_template(
                        "partials/ai_content_results.html", results=result
                    ),
                }
            )

        except Exception as e:
            return jsonify(
                {"success": False, "error": f"Optimization failed: {str(e)}"}
            )

    # GET request - show the tool interface
    tool_data = {
        "tool_name": "AI Content Optimizer Pro",
        "tool_description": "Professional AI-powered content optimization using advanced machine learning models. Analyze readability, SEO score, keyword density, and get actionable improvement suggestions.",
        "is_ai_tool": True,
        "is_pro_required": True,
        "tool_features": [
            "Advanced AI Analysis",
            "SEO Score Calculation",
            "Keyword Optimization",
            "Readability Enhancement",
            "Content Structure Analysis",
            "Competitive Intelligence",
            "Export Reports",
        ],
        "tool_guide_steps": [
            "Paste your content into the text area (articles, blog posts, web pages)",
            "Enter your target keywords separated by commas",
            "Select content type for specialized analysis",
            "Choose optimization level based on your needs",
            'Click "Optimize with AI" to get comprehensive analysis',
            "Review AI-generated suggestions and improvements",
            "Export your optimization report in multiple formats",
        ],
        "related_tools": [
            {
                "name": "AI Keyword Research Pro",
                "url": "/tools/ai-keyword-research",
                "description": "Advanced keyword analysis",
            },
            {
                "name": "SEO Score Calculator",
                "url": "/tools/seo-score-calculator",
                "description": "Comprehensive SEO scoring",
            },
            {
                "name": "Content Gap Analyzer",
                "url": "/tools/content-gap-analyzer",
                "description": "Identify content opportunities",
            },
        ],
    }

    return render_template("tools/ai_content_optimizer.html", **tool_data)


def optimize_content_with_ai(
    content, target_keywords, content_type, optimization_level
):
    """
    Use OpenRouter API to optimize content with AI
    """
    try:
        # Get OpenRouter API keys
        api_keys = os.getenv("OPENROUTER_API_KEYS", "").split(",")
        if not api_keys or not api_keys[0]:
            raise Exception("OpenRouter API key not configured")

        # Prepare the optimization prompt
        prompt = f"""
        As an expert SEO content optimizer, analyze and optimize the following content:

        CONTENT TYPE: {content_type}
        TARGET KEYWORDS: {target_keywords}
        OPTIMIZATION LEVEL: {optimization_level}

        CONTENT TO OPTIMIZE:
        {content}

        Please provide a comprehensive analysis including:

        1. SEO SCORE (0-100) with detailed breakdown
        2. KEYWORD OPTIMIZATION ANALYSIS
        3. READABILITY ASSESSMENT (Flesch score, grade level)
        4. CONTENT STRUCTURE EVALUATION
        5. SPECIFIC IMPROVEMENT RECOMMENDATIONS
        6. OPTIMIZED VERSION SUGGESTIONS
        7. COMPETITIVE INSIGHTS
        8. TECHNICAL SEO RECOMMENDATIONS

        Format your response as structured JSON with clear metrics and actionable advice.
        """

        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {api_keys[0].strip()}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "meta-llama/llama-3.1-70b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert SEO content optimization specialist with deep knowledge of search engine algorithms, content marketing, and technical SEO.",
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
            ai_response = result["choices"][0]["message"]["content"]

            # Parse and structure the response
            optimization_result = parse_optimization_response(
                ai_response, content, target_keywords
            )
            return optimization_result
        else:
            raise Exception(f"API request failed: {response.status_code}")

    except Exception as e:
        # Fallback to basic analysis if AI fails
        return generate_fallback_analysis(content, target_keywords, content_type)


def parse_optimization_response(ai_response, original_content, target_keywords):
    """
    Parse and structure the AI optimization response
    """
    try:
        # Try to extract JSON from response
        if "```json" in ai_response:
            json_start = ai_response.find("```json") + 7
            json_end = ai_response.find("```", json_start)
            json_str = ai_response[json_start:json_end].strip()
            structured_data = json.loads(json_str)
        else:
            # Parse unstructured response
            structured_data = {
                "seo_score": extract_score_from_text(ai_response),
                "analysis": ai_response,
                "recommendations": extract_recommendations_from_text(ai_response),
            }

        # Add metadata
        structured_data.update(
            {
                "word_count": len(original_content.split()),
                "character_count": len(original_content),
                "target_keywords": (
                    target_keywords.split(",") if target_keywords else []
                ),
                "analysis_timestamp": datetime.now().isoformat(),
                "tool_version": "2.0 Professional",
            }
        )

        return structured_data

    except Exception as e:
        return {
            "seo_score": 75,
            "analysis": ai_response,
            "recommendations": ["Review AI analysis above for detailed insights"],
            "word_count": len(original_content.split()),
            "character_count": len(original_content),
            "error": f"Parsing error: {str(e)}",
        }


def extract_score_from_text(text):
    """Extract SEO score from text"""
    import re

    score_match = re.search(r"(\d+)/100|(\d+)%", text)
    return int(score_match.group(1) or score_match.group(2)) if score_match else 75


def extract_recommendations_from_text(text):
    """Extract recommendations from text"""
    lines = text.split("\n")
    recommendations = []
    for line in lines:
        if (
            "recommend" in line.lower()
            or "improve" in line.lower()
            or "optimize" in line.lower()
            or line.strip().startswith("-")
            or line.strip().startswith("•")
        ):
            recommendations.append(line.strip())
    return recommendations[:10]  # Limit to top 10


def generate_fallback_analysis(content, target_keywords, content_type):
    """
    Generate basic analysis if AI fails
    """
    words = content.split()
    word_count = len(words)
    char_count = len(content)

    # Basic keyword density calculation
    keyword_density = {}
    if target_keywords:
        for keyword in target_keywords.split(","):
            keyword = keyword.strip().lower()
            count = content.lower().count(keyword)
            density = (count / word_count) * 100 if word_count > 0 else 0
            keyword_density[keyword] = {"count": count, "density": round(density, 2)}

    return {
        "seo_score": 78,
        "word_count": word_count,
        "character_count": char_count,
        "keyword_density": keyword_density,
        "recommendations": [
            "Optimize content length for better SEO performance",
            "Improve keyword distribution throughout the content",
            "Add more relevant subheadings and structure",
            "Include internal and external links",
            "Optimize meta descriptions and title tags",
        ],
        "readability": {
            "grade_level": "College" if word_count > 500 else "High School",
            "estimated_reading_time": max(1, word_count // 200),
        },
        "analysis_timestamp": datetime.now().isoformat(),
        "fallback_mode": True,
    }
