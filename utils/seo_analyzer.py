"""
Enhanced SEO Analysis Engine
Advanced SEO analysis with AI-powered recommendations
"""

import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json
import hashlib
import time

from flask import current_app
from utils.caching import cached, cache_database_query
from utils.advanced_caching import get_smart_cache_manager


class SEOAnalyzer:
    """Advanced SEO analysis engine with comprehensive checks"""

    def __init__(self):
        self.smart_cache = get_smart_cache_manager()
        self.user_agent = (
            "Mozilla/5.0 (compatible; SEO-Toolkit-Bot/1.0; +https://example.com/bot)"
        )

        # SEO scoring weights
        self.scoring_weights = {
            "title": 15,
            "meta_description": 10,
            "headings": 12,
            "content_quality": 20,
            "technical": 15,
            "performance": 10,
            "mobile": 8,
            "security": 5,
            "accessibility": 5,
        }

    def analyze_url(self, url: str, deep_analysis: bool = False) -> Dict[str, Any]:
        """
        Comprehensive SEO analysis of a URL

        Args:
            url: URL to analyze
            deep_analysis: Whether to perform deep technical analysis

        Returns:
            Complete SEO analysis report
        """
        analysis_start = time.time()

        try:
            # Generate cache key
            cache_key = f"seo_analysis:{hashlib.md5(url.encode()).hexdigest()}"
            if deep_analysis:
                cache_key += ":deep"

            # Try to get cached analysis
            cached_result = self.smart_cache.intelligent_get(
                cache_key,
                fetch_func=lambda: self._perform_analysis(url, deep_analysis),
                ttl=3600,  # Cache for 1 hour
            )

            if cached_result:
                cached_result["cached"] = True
                cached_result["analysis_time"] = time.time() - analysis_start
                return cached_result

            # Perform fresh analysis
            result = self._perform_analysis(url, deep_analysis)
            result["cached"] = False
            result["analysis_time"] = time.time() - analysis_start

            return result

        except Exception as e:
            return {
                "error": str(e),
                "url": url,
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
            }

    def _perform_analysis(self, url: str, deep_analysis: bool) -> Dict[str, Any]:
        """Perform the actual SEO analysis"""

        # Fetch page content
        page_data = self._fetch_page(url)
        if "error" in page_data:
            return page_data

        soup = page_data["soup"]
        response = page_data["response"]

        # Initialize analysis results
        analysis = {
            "url": url,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0,
            "categories": {},
        }

        # Perform analysis categories
        analysis["categories"]["title"] = self._analyze_title(soup)
        analysis["categories"]["meta_description"] = self._analyze_meta_description(
            soup
        )
        analysis["categories"]["headings"] = self._analyze_headings(soup)
        analysis["categories"]["content"] = self._analyze_content(soup, url)
        analysis["categories"]["technical"] = self._analyze_technical(
            soup, response, url
        )
        analysis["categories"]["images"] = self._analyze_images(soup, url)
        analysis["categories"]["links"] = self._analyze_links(soup, url)

        if deep_analysis:
            analysis["categories"]["performance"] = self._analyze_performance(
                url, response
            )
            analysis["categories"]["mobile"] = self._analyze_mobile_friendliness(soup)
            analysis["categories"]["security"] = self._analyze_security(url, response)
            analysis["categories"]["accessibility"] = self._analyze_accessibility(soup)

        # Calculate overall score
        analysis["overall_score"] = self._calculate_overall_score(
            analysis["categories"]
        )

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(
            analysis["categories"]
        )

        # Add summary
        analysis["summary"] = self._generate_summary(analysis)

        return analysis

    def _fetch_page(self, url: str) -> Dict[str, Any]:
        """Fetch and parse the webpage"""
        try:
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }

            response = requests.get(
                url, headers=headers, timeout=30, allow_redirects=True
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            return {
                "soup": soup,
                "response": response,
                "final_url": response.url,
                "status_code": response.status_code,
            }

        except Exception as e:
            return {
                "error": f"Failed to fetch URL: {str(e)}",
                "url": url,
                "status": "fetch_failed",
            }

    def _analyze_title(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page title"""
        title_tag = soup.find("title")

        if not title_tag:
            return {
                "score": 0,
                "status": "missing",
                "issues": ["No title tag found"],
                "recommendations": ["Add a descriptive title tag"],
            }

        title = title_tag.get_text().strip()
        length = len(title)

        # Scoring based on title quality
        score = 50  # Base score for having a title
        issues = []
        recommendations = []

        # Length check
        if length == 0:
            score = 0
            issues.append("Title is empty")
            recommendations.append("Add a descriptive title")
        elif length < 30:
            score -= 20
            issues.append("Title is too short (less than 30 characters)")
            recommendations.append("Expand title to 30-60 characters for better SEO")
        elif length > 60:
            score -= 15
            issues.append("Title is too long (over 60 characters)")
            recommendations.append(
                "Shorten title to under 60 characters to avoid truncation"
            )
        else:
            score += 30  # Good length

        # Content quality checks
        if title.lower() == title:
            score -= 10
            issues.append("Title is all lowercase")
            recommendations.append("Use proper capitalization in title")

        if "|" in title or "-" in title:
            score += 10  # Brand separation is good

        # Check for keywords (basic analysis)
        word_count = len(title.split())
        if word_count < 3:
            score -= 10
            issues.append("Title has very few words")
            recommendations.append("Include more descriptive keywords in title")

        return {
            "score": max(0, min(100, score)),
            "title": title,
            "length": length,
            "word_count": word_count,
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_meta_description(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze meta description"""
        meta_desc = soup.find("meta", attrs={"name": "description"})

        if not meta_desc:
            return {
                "score": 0,
                "status": "missing",
                "issues": ["No meta description found"],
                "recommendations": [
                    "Add a compelling meta description (150-160 characters)"
                ],
            }

        description = meta_desc.get("content", "").strip()
        length = len(description)

        score = 40  # Base score for having meta description
        issues = []
        recommendations = []

        # Length analysis
        if length == 0:
            score = 0
            issues.append("Meta description is empty")
            recommendations.append("Add a compelling meta description")
        elif length < 120:
            score -= 15
            issues.append("Meta description is too short")
            recommendations.append("Expand meta description to 150-160 characters")
        elif length > 160:
            score -= 20
            issues.append("Meta description is too long (may be truncated)")
            recommendations.append("Shorten meta description to under 160 characters")
        else:
            score += 40  # Good length

        # Content quality
        if (
            description
            and not description.endswith(".")
            and not description.endswith("!")
            and not description.endswith("?")
        ):
            score -= 5
            recommendations.append("End meta description with proper punctuation")

        return {
            "score": max(0, min(100, score)),
            "description": description,
            "length": length,
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_headings(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading structure"""
        headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}

        for level in headings.keys():
            tags = soup.find_all(level)
            headings[level] = [tag.get_text().strip() for tag in tags]

        score = 50
        issues = []
        recommendations = []

        # H1 analysis
        h1_count = len(headings["h1"])
        if h1_count == 0:
            score -= 30
            issues.append("No H1 tag found")
            recommendations.append("Add exactly one H1 tag with your main keyword")
        elif h1_count > 1:
            score -= 15
            issues.append(f"Multiple H1 tags found ({h1_count})")
            recommendations.append("Use only one H1 tag per page")
        else:
            score += 20  # Perfect H1 usage

        # Heading hierarchy
        total_headings = sum(len(headings[level]) for level in headings.keys())
        if total_headings < 3:
            score -= 15
            issues.append("Very few headings - poor content structure")
            recommendations.append("Add more headings to improve content structure")

        # Check for logical hierarchy
        if headings["h2"] and not headings["h1"]:
            score -= 10
            issues.append("H2 tags without H1")
            recommendations.append("Add H1 before using H2 tags")

        return {
            "score": max(0, min(100, score)),
            "headings": headings,
            "total_count": total_headings,
            "h1_count": h1_count,
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analyze content quality and structure"""

        # Extract main content (remove scripts, styles, nav, footer)
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text_content = soup.get_text()
        words = text_content.split()
        word_count = len(words)

        score = 30
        issues = []
        recommendations = []

        # Word count analysis
        if word_count < 300:
            score -= 25
            issues.append(f"Content is too short ({word_count} words)")
            recommendations.append("Add more content - aim for at least 300 words")
        elif word_count < 500:
            score -= 10
            issues.append("Content could be more comprehensive")
            recommendations.append("Consider expanding content for better SEO value")
        else:
            score += 30  # Good content length

        # Paragraph analysis
        paragraphs = soup.find_all("p")
        if len(paragraphs) < 3:
            score -= 15
            issues.append("Very few paragraphs - poor content structure")
            recommendations.append(
                "Break content into more paragraphs for better readability"
            )

        # Check for lists (good for SEO)
        lists = soup.find_all(["ul", "ol"])
        if lists:
            score += 10
        else:
            recommendations.append("Consider adding bullet points or numbered lists")

        # Image-to-text ratio
        images = soup.find_all("img")
        if len(images) == 0 and word_count > 500:
            score -= 10
            recommendations.append("Add relevant images to break up text content")

        return {
            "score": max(0, min(100, score)),
            "word_count": word_count,
            "paragraph_count": len(paragraphs),
            "list_count": len(lists),
            "image_count": len(images),
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_technical(
        self, soup: BeautifulSoup, response: requests.Response, url: str
    ) -> Dict[str, Any]:
        """Analyze technical SEO factors"""
        score = 60
        issues = []
        recommendations = []

        # Check for canonical URL
        canonical = soup.find("link", rel="canonical")
        if not canonical:
            score -= 15
            issues.append("No canonical URL specified")
            recommendations.append(
                "Add canonical URL to avoid duplicate content issues"
            )

        # Check for meta viewport (mobile)
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            score -= 10
            issues.append("No viewport meta tag found")
            recommendations.append("Add viewport meta tag for mobile optimization")

        # Check for schema markup
        scripts = soup.find_all("script", type="application/ld+json")
        if not scripts:
            score -= 10
            issues.append("No structured data (schema markup) found")
            recommendations.append(
                "Add structured data markup for better search visibility"
            )
        else:
            score += 10

        # Check response time (basic)
        if hasattr(response, "elapsed"):
            response_time = response.elapsed.total_seconds()
            if response_time > 3:
                score -= 15
                issues.append(f"Slow response time ({response_time:.2f}s)")
                recommendations.append(
                    "Optimize server response time to under 3 seconds"
                )
            elif response_time > 1:
                score -= 5
                issues.append("Response time could be improved")

        # Check for HTTPS
        if not url.startswith("https://"):
            score -= 20
            issues.append("Site is not using HTTPS")
            recommendations.append("Enable HTTPS for security and SEO benefits")
        else:
            score += 10

        return {
            "score": max(0, min(100, score)),
            "has_canonical": canonical is not None,
            "has_viewport": viewport is not None,
            "has_schema": len(scripts) > 0,
            "is_https": url.startswith("https://"),
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_images(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analyze image optimization"""
        images = soup.find_all("img")

        score = 70  # Start with good score
        issues = []
        recommendations = []

        missing_alt = 0
        total_images = len(images)

        if total_images == 0:
            return {
                "score": 100,
                "total_images": 0,
                "status": "no_images",
                "issues": [],
                "recommendations": [
                    "Consider adding relevant images to enhance content"
                ],
            }

        for img in images:
            alt_text = img.get("alt", "").strip()
            if not alt_text:
                missing_alt += 1

        # Calculate score based on alt text coverage
        if missing_alt > 0:
            alt_coverage = (total_images - missing_alt) / total_images
            score = int(70 * alt_coverage)

            if missing_alt == total_images:
                issues.append("No images have alt text")
                recommendations.append("Add descriptive alt text to all images")
            else:
                issues.append(f"{missing_alt} images missing alt text")
                recommendations.append("Add alt text to remaining images")
        else:
            score = 100  # Perfect alt text coverage

        return {
            "score": max(0, min(100, score)),
            "total_images": total_images,
            "missing_alt": missing_alt,
            "alt_coverage": (
                (total_images - missing_alt) / total_images if total_images > 0 else 0
            ),
            "status": (
                "good"
                if score >= 80
                else "needs_improvement" if score >= 50 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_links(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analyze internal and external links"""
        links = soup.find_all("a", href=True)

        internal_links = []
        external_links = []
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc

        for link in links:
            href = link["href"]
            absolute_url = urljoin(url, href)
            parsed_link = urlparse(absolute_url)

            if parsed_link.netloc == base_domain or not parsed_link.netloc:
                internal_links.append(href)
            else:
                external_links.append(href)

        score = 60
        issues = []
        recommendations = []

        # Check link quantities
        if len(internal_links) < 3:
            score -= 15
            issues.append("Very few internal links")
            recommendations.append("Add more internal links to improve site navigation")

        if len(external_links) == 0:
            score -= 10
            recommendations.append(
                "Consider adding relevant external links for authority"
            )
        elif len(external_links) > 10:
            score -= 5
            recommendations.append("Too many external links - consider reducing")

        # Check for broken link patterns (basic)
        suspicious_links = [
            link for link in links if not link.get("href") or link["href"] == "#"
        ]
        if suspicious_links:
            score -= 10
            issues.append(f"{len(suspicious_links)} links may be broken or incomplete")
            recommendations.append("Review and fix broken or incomplete links")

        return {
            "score": max(0, min(100, score)),
            "total_links": len(links),
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "suspicious_links": len(suspicious_links),
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_performance(
        self, url: str, response: requests.Response
    ) -> Dict[str, Any]:
        """Basic performance analysis"""
        score = 60
        issues = []
        recommendations = []

        # Response time
        if hasattr(response, "elapsed"):
            response_time = response.elapsed.total_seconds()
            if response_time > 3:
                score -= 30
                issues.append(f"Very slow response time: {response_time:.2f}s")
                recommendations.append("Optimize server performance and caching")
            elif response_time > 1:
                score -= 15
                issues.append(f"Slow response time: {response_time:.2f}s")
                recommendations.append("Consider performance optimizations")
            else:
                score += 20

        # Content size
        content_length = len(response.content)
        if content_length > 1024 * 1024:  # 1MB
            score -= 15
            issues.append("Large page size may affect loading speed")
            recommendations.append("Optimize images and minimize CSS/JS")

        return {
            "score": max(0, min(100, score)),
            "response_time": (
                response.elapsed.total_seconds()
                if hasattr(response, "elapsed")
                else None
            ),
            "content_size": content_length,
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_mobile_friendliness(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze mobile optimization"""
        score = 50
        issues = []
        recommendations = []

        # Viewport meta tag
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if viewport:
            score += 30
        else:
            issues.append("No viewport meta tag")
            recommendations.append("Add viewport meta tag for mobile optimization")

        # Check for responsive framework indicators
        css_links = soup.find_all("link", rel="stylesheet")
        responsive_indicators = ["bootstrap", "foundation", "responsive", "mobile"]

        for link in css_links:
            href = link.get("href", "").lower()
            if any(indicator in href for indicator in responsive_indicators):
                score += 10
                break

        return {
            "score": max(0, min(100, score)),
            "has_viewport": viewport is not None,
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_security(
        self, url: str, response: requests.Response
    ) -> Dict[str, Any]:
        """Analyze security factors"""
        score = 60
        issues = []
        recommendations = []

        # HTTPS check
        if url.startswith("https://"):
            score += 30
        else:
            score -= 30
            issues.append("Site is not using HTTPS")
            recommendations.append("Enable HTTPS for security and SEO")

        # Security headers check
        headers = response.headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
        ]

        for header in security_headers:
            if header in headers:
                score += 5
            else:
                recommendations.append(f"Add {header} security header")

        return {
            "score": max(0, min(100, score)),
            "is_https": url.startswith("https://"),
            "security_headers": len([h for h in security_headers if h in headers]),
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Basic accessibility analysis"""
        score = 60
        issues = []
        recommendations = []

        # Check for alt text on images
        images = soup.find_all("img")
        images_with_alt = [img for img in images if img.get("alt")]

        if images:
            alt_coverage = len(images_with_alt) / len(images)
            if alt_coverage < 0.5:
                score -= 20
                issues.append("Many images missing alt text")
                recommendations.append("Add alt text to all images for accessibility")
            elif alt_coverage < 1:
                score -= 10
                recommendations.append("Add alt text to remaining images")
            else:
                score += 20

        # Check for heading structure
        h1_tags = soup.find_all("h1")
        if len(h1_tags) != 1:
            score -= 10
            issues.append("Poor heading structure for screen readers")
            recommendations.append("Use proper heading hierarchy with one H1")

        return {
            "score": max(0, min(100, score)),
            "images_with_alt": len(images_with_alt),
            "total_images": len(images),
            "status": (
                "good"
                if score >= 70
                else "needs_improvement" if score >= 40 else "poor"
            ),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _calculate_overall_score(self, categories: Dict[str, Dict]) -> int:
        """Calculate weighted overall SEO score"""
        total_score = 0
        total_weight = 0

        for category, weight in self.scoring_weights.items():
            if category in categories and "score" in categories[category]:
                total_score += categories[category]["score"] * weight
                total_weight += weight

        return int(total_score / total_weight) if total_weight > 0 else 0

    def _generate_recommendations(
        self, categories: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations"""
        recommendations = []

        for category, data in categories.items():
            if "recommendations" in data and data["recommendations"]:
                priority = self._get_recommendation_priority(
                    category, data.get("score", 0)
                )

                for rec in data["recommendations"]:
                    recommendations.append(
                        {
                            "category": category,
                            "recommendation": rec,
                            "priority": priority,
                            "impact": self.scoring_weights.get(category, 5),
                        }
                    )

        # Sort by priority and impact
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(
            key=lambda x: (priority_order.get(x["priority"], 3), -x["impact"])
        )

        return recommendations[:10]  # Return top 10 recommendations

    def _get_recommendation_priority(self, category: str, score: int) -> str:
        """Determine recommendation priority based on category importance and score"""
        if score < 40:
            return "high"
        elif score < 70:
            return "medium"
        else:
            return "low"

    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary"""
        overall_score = analysis["overall_score"]
        categories = analysis["categories"]

        # Determine overall status
        if overall_score >= 80:
            status = "excellent"
            status_message = "Your page has excellent SEO optimization!"
        elif overall_score >= 60:
            status = "good"
            status_message = "Your page has good SEO with room for improvement."
        elif overall_score >= 40:
            status = "needs_improvement"
            status_message = "Your page needs significant SEO improvements."
        else:
            status = "poor"
            status_message = (
                "Your page has critical SEO issues that need immediate attention."
            )

        # Find best and worst categories
        category_scores = {
            cat: data.get("score", 0)
            for cat, data in categories.items()
            if "score" in data
        }
        best_category = (
            max(category_scores.items(), key=lambda x: x[1])
            if category_scores
            else None
        )
        worst_category = (
            min(category_scores.items(), key=lambda x: x[1])
            if category_scores
            else None
        )

        return {
            "overall_score": overall_score,
            "status": status,
            "status_message": status_message,
            "best_category": (
                {"name": best_category[0], "score": best_category[1]}
                if best_category
                else None
            ),
            "worst_category": (
                {"name": worst_category[0], "score": worst_category[1]}
                if worst_category
                else None
            ),
            "total_recommendations": len(analysis.get("recommendations", [])),
            "high_priority_issues": len(
                [
                    r
                    for r in analysis.get("recommendations", [])
                    if r["priority"] == "high"
                ]
            ),
        }


# Utility functions for SEO analysis
def analyze_url_seo(url: str, deep_analysis: bool = False) -> Dict[str, Any]:
    """Convenience function for SEO analysis"""
    analyzer = SEOAnalyzer()
    return analyzer.analyze_url(url, deep_analysis)


def bulk_analyze_urls(urls: List[str], deep_analysis: bool = False) -> Dict[str, Any]:
    """Analyze multiple URLs in batch"""
    analyzer = SEOAnalyzer()
    results = {}

    for url in urls:
        try:
            results[url] = analyzer.analyze_url(url, deep_analysis)
        except Exception as e:
            results[url] = {"error": str(e), "status": "failed", "url": url}

    return {
        "batch_results": results,
        "total_analyzed": len(urls),
        "successful": len(
            [r for r in results.values() if r.get("status") == "success"]
        ),
        "failed": len([r for r in results.values() if r.get("status") == "failed"]),
        "timestamp": datetime.now().isoformat(),
    }
