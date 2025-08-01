"""
Premium SEO Features - Advanced Analytics for Pro Users
Includes competitor analysis, historical tracking, and advanced insights
"""

import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse
import json
import time
from bs4 import BeautifulSoup


class PremiumSEOFeatures:
    """Advanced SEO features exclusively for premium users"""

    def __init__(self, base_url, user_id=None):
        self.base_url = base_url.rstrip("/")
        self.domain = urlparse(base_url).netloc
        self.user_id = user_id
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def analyze_competitors(self, competitor_urls=None):
        """Analyze competitor websites for benchmarking"""
        if not competitor_urls:
            # Auto-discover competitors based on industry keywords
            competitor_urls = self.discover_competitors()

        competitor_analysis = {
            "timestamp": datetime.now().isoformat(),
            "main_domain": self.domain,
            "competitors": {},
            "benchmarks": {},
            "opportunities": [],
        }

        # Analyze each competitor
        for comp_url in competitor_urls[:3]:  # Limit to 3 competitors
            try:
                comp_domain = urlparse(comp_url).netloc
                print(f"🔍 Analyzing competitor: {comp_domain}")

                # Basic SEO metrics comparison
                comp_metrics = self.get_competitor_metrics(comp_url)
                competitor_analysis["competitors"][comp_domain] = comp_metrics

                # Find gaps and opportunities
                opportunities = self.identify_content_gaps(comp_url)
                competitor_analysis["opportunities"].extend(opportunities)

            except Exception as e:
                print(f"⚠️  Failed to analyze {comp_url}: {str(e)}")

        # Generate benchmarks
        competitor_analysis["benchmarks"] = self.calculate_benchmarks(
            competitor_analysis["competitors"]
        )

        return competitor_analysis

    def get_competitor_metrics(self, competitor_url):
        """Extract key SEO metrics from competitor"""
        try:
            response = requests.get(competitor_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.content, "html.parser")

            metrics = {
                "title_length": len(soup.title.string) if soup.title else 0,
                "meta_description": bool(
                    soup.find("meta", attrs={"name": "description"})
                ),
                "h1_count": len(soup.find_all("h1")),
                "h2_count": len(soup.find_all("h2")),
                "internal_links": len(
                    [
                        a
                        for a in soup.find_all("a", href=True)
                        if urlparse(competitor_url).netloc in a["href"]
                    ]
                ),
                "external_links": len(
                    [
                        a
                        for a in soup.find_all("a", href=True)
                        if urlparse(competitor_url).netloc not in a["href"]
                        and a["href"].startswith("http")
                    ]
                ),
                "images_without_alt": len(
                    [img for img in soup.find_all("img") if not img.get("alt")]
                ),
                "schema_markup": bool(soup.find("script", type="application/ld+json")),
                "page_load_time": self.estimate_load_time(competitor_url),
                "content_length": len(soup.get_text().strip()),
                "keywords_density": self.analyze_keyword_density(soup.get_text()),
            }

            return metrics

        except Exception as e:
            return {"error": str(e)}

    def discover_competitors(self):
        """Auto-discover potential competitors"""
        # This would typically use APIs like SEMrush, Ahrefs, or similar services
        # For demo purposes, we'll use common competitors based on domain patterns

        common_competitors = [
            "https://github.com",
            "https://stackoverflow.com",
            "https://google.com",
        ]

        return common_competitors

    def historical_tracking(self, days_back=30):
        """Track SEO metrics over time for trend analysis"""
        from app.models.seo_reports import SEOReport
        from app.core.extensions import db

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Get historical reports for this domain
        historical_reports = (
            SEOReport.query.filter(
                SEOReport.website_url.like(f"%{self.domain}%"),
                SEOReport.created_at >= start_date,
                SEOReport.created_at <= end_date,
            )
            .order_by(SEOReport.created_at.desc())
            .all()
        )

        if not historical_reports:
            return self.generate_sample_historical_data()

        trends = {
            "domain": self.domain,
            "period": f"{days_back} days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data_points": len(historical_reports),
            "trends": {
                "overall_score": [],
                "technical_seo": [],
                "content_quality": [],
                "performance": [],
                "recommendations_count": [],
            },
            "insights": [],
        }

        # Process historical data
        for report in historical_reports:
            trends["trends"]["overall_score"].append(
                {"date": report.created_at.isoformat(), "value": report.overall_score}
            )

            # Parse audit data if available
            if report.audit_data:
                try:
                    audit_data = (
                        json.loads(report.audit_data)
                        if isinstance(report.audit_data, str)
                        else report.audit_data
                    )

                    # Extract trend data
                    score_breakdown = audit_data.get("score_breakdown", {})
                    trends["trends"]["technical_seo"].append(
                        {
                            "date": report.created_at.isoformat(),
                            "value": score_breakdown.get("technical_seo", 0),
                        }
                    )
                    trends["trends"]["content_quality"].append(
                        {
                            "date": report.created_at.isoformat(),
                            "value": score_breakdown.get("content_analysis", 0),
                        }
                    )
                    trends["trends"]["performance"].append(
                        {
                            "date": report.created_at.isoformat(),
                            "value": score_breakdown.get("performance", 0),
                        }
                    )

                    # Count recommendations
                    recs = audit_data.get("recommendations", {})
                    total_recs = sum(
                        len(items) for items in recs.values() if isinstance(items, list)
                    )
                    trends["trends"]["recommendations_count"].append(
                        {"date": report.created_at.isoformat(), "value": total_recs}
                    )

                except Exception as e:
                    print(f"Error parsing historical data: {e}")

        # Generate insights
        trends["insights"] = self.generate_trend_insights(trends["trends"])

        return trends

    def generate_trend_insights(self, trends_data):
        """Generate actionable insights from trend data"""
        insights = []

        # Overall Score Trend
        overall_scores = [
            point["value"] for point in trends_data.get("overall_score", [])
        ]
        if len(overall_scores) >= 2:
            score_change = overall_scores[0] - overall_scores[-1]  # Latest - Oldest
            if score_change > 5:
                insights.append(
                    {
                        "type": "positive",
                        "category": "Overall Performance",
                        "message": f"SEO score improved by {score_change:.1f} points",
                        "recommendation": "Continue current optimization efforts",
                    }
                )
            elif score_change < -5:
                insights.append(
                    {
                        "type": "negative",
                        "category": "Overall Performance",
                        "message": f"SEO score declined by {abs(score_change):.1f} points",
                        "recommendation": "Review recent changes and address critical issues",
                    }
                )

        # Technical SEO Trend
        tech_scores = [point["value"] for point in trends_data.get("technical_seo", [])]
        if len(tech_scores) >= 2:
            tech_change = tech_scores[0] - tech_scores[-1]
            if tech_change < -3:
                insights.append(
                    {
                        "type": "alert",
                        "category": "Technical SEO",
                        "message": "Technical SEO score is declining",
                        "recommendation": "Check for broken links, SSL issues, or crawling problems",
                    }
                )

        # Recommendations Trend
        rec_counts = [
            point["value"] for point in trends_data.get("recommendations_count", [])
        ]
        if len(rec_counts) >= 2:
            if rec_counts[0] > rec_counts[-1]:
                insights.append(
                    {
                        "type": "alert",
                        "category": "Issues",
                        "message": "Number of SEO issues is increasing",
                        "recommendation": "Address high-priority recommendations to prevent further degradation",
                    }
                )

        return insights

    def generate_sample_historical_data(self):
        """Generate sample historical data for demo purposes"""
        return {
            "domain": self.domain,
            "period": "30 days",
            "data_points": 0,
            "message": "No historical data available yet. Run regular audits to build trend analysis.",
            "trends": {
                "overall_score": [],
                "technical_seo": [],
                "content_quality": [],
                "performance": [],
                "recommendations_count": [],
            },
            "insights": [
                {
                    "type": "info",
                    "category": "Getting Started",
                    "message": "Start tracking your SEO progress",
                    "recommendation": "Run weekly audits to build comprehensive trend data",
                }
            ],
        }

    def advanced_keyword_analysis(self):
        """Advanced keyword analysis and opportunities"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.content, "html.parser")
            text_content = soup.get_text().lower()

            # Extract potential keywords
            words = text_content.split()
            word_freq = {}

            # Filter meaningful words (3+ characters, not common stop words)
            stop_words = {
                "the",
                "and",
                "for",
                "are",
                "but",
                "not",
                "you",
                "all",
                "can",
                "had",
                "her",
                "was",
                "one",
                "our",
                "out",
                "day",
                "get",
                "has",
                "him",
                "his",
                "how",
                "its",
                "may",
                "new",
                "now",
                "old",
                "see",
                "two",
                "way",
                "who",
                "boy",
                "did",
                "man",
                "end",
                "few",
                "got",
                "let",
                "put",
                "say",
                "she",
                "too",
                "use",
            }

            for word in words:
                # Clean word
                clean_word = "".join(c for c in word if c.isalnum())
                if len(clean_word) >= 3 and clean_word not in stop_words:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1

            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[
                :20
            ]

            # Analyze keyword optimization
            title = soup.title.string if soup.title else ""
            meta_desc = soup.find("meta", attrs={"name": "description"})
            meta_desc_text = meta_desc["content"] if meta_desc else ""

            keyword_analysis = {
                "top_keywords": [
                    {"keyword": k, "frequency": f} for k, f in top_keywords
                ],
                "title_keywords": [k for k, f in top_keywords if k in title.lower()],
                "meta_keywords": [
                    k for k, f in top_keywords if k in meta_desc_text.lower()
                ],
                "opportunities": [],
                "optimization_score": 0,
            }

            # Generate optimization opportunities
            high_freq_keywords = [k for k, f in top_keywords[:5]]

            for keyword in high_freq_keywords:
                if keyword not in title.lower():
                    keyword_analysis["opportunities"].append(
                        {
                            "type": "Title Optimization",
                            "keyword": keyword,
                            "suggestion": f"Consider including '{keyword}' in your page title",
                            "priority": "high",
                        }
                    )

                if keyword not in meta_desc_text.lower():
                    keyword_analysis["opportunities"].append(
                        {
                            "type": "Meta Description",
                            "keyword": keyword,
                            "suggestion": f"Include '{keyword}' in your meta description",
                            "priority": "medium",
                        }
                    )

            # Calculate optimization score
            title_score = len(keyword_analysis["title_keywords"]) * 20
            meta_score = len(keyword_analysis["meta_keywords"]) * 15
            keyword_analysis["optimization_score"] = min(100, title_score + meta_score)

            return keyword_analysis

        except Exception as e:
            return {"error": str(e)}

    def estimate_load_time(self, url):
        """Estimate page load time"""
        try:
            start_time = time.time()
            response = requests.get(url, headers=self.headers, timeout=10)
            load_time = round(
                (time.time() - start_time) * 1000, 2
            )  # Convert to milliseconds
            return load_time
        except:
            return None

    def analyze_keyword_density(self, text):
        """Analyze keyword density in content"""
        words = text.lower().split()
        total_words = len(words)

        if total_words == 0:
            return {}

        word_count = {}
        for word in words:
            clean_word = "".join(c for c in word if c.isalnum())
            if len(clean_word) >= 3:
                word_count[clean_word] = word_count.get(clean_word, 0) + 1

        # Calculate density for top words
        densities = {}
        for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]:
            density = round((count / total_words) * 100, 2)
            densities[word] = density

        return densities

    def identify_content_gaps(self, competitor_url):
        """Identify content opportunities based on competitor analysis"""
        opportunities = []

        try:
            response = requests.get(competitor_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Analyze competitor's headings for content topics
                headings = []
                for h in soup.find_all(["h1", "h2", "h3"]):
                    if h.get_text().strip():
                        headings.append(h.get_text().strip())

                # Generate content gap opportunities
                if headings:
                    opportunities.append(
                        {
                            "type": "Content Topics",
                            "competitor": urlparse(competitor_url).netloc,
                            "suggestion": f"Consider creating content around: {', '.join(headings[:3])}",
                            "priority": "medium",
                        }
                    )

        except Exception as e:
            pass

        return opportunities

    def calculate_benchmarks(self, competitors_data):
        """Calculate industry benchmarks from competitor data"""
        if not competitors_data:
            return {}

        benchmarks = {}
        metrics = [
            "title_length",
            "h1_count",
            "h2_count",
            "internal_links",
            "content_length",
        ]

        for metric in metrics:
            values = []
            for comp_data in competitors_data.values():
                if metric in comp_data and isinstance(comp_data[metric], (int, float)):
                    values.append(comp_data[metric])

            if values:
                benchmarks[metric] = {
                    "average": round(sum(values) / len(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "recommendation": self.get_benchmark_recommendation(metric, values),
                }

        return benchmarks

    def get_benchmark_recommendation(self, metric, values):
        """Get recommendations based on benchmark data"""
        avg = sum(values) / len(values)

        recommendations = {
            "title_length": f"Optimal title length: 50-60 characters (industry avg: {avg:.0f})",
            "h1_count": f"Use 1 H1 tag per page (industry avg: {avg:.1f})",
            "h2_count": f"Structure content with H2 tags (industry avg: {avg:.0f})",
            "internal_links": f"Include {max(5, int(avg))} internal links per page",
            "content_length": f"Aim for {max(300, int(avg))} words of quality content",
        }

        return recommendations.get(metric, f"Industry average: {avg:.2f}")
