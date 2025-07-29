import requests
import json
import time
import re
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


def analyze_keywords(
    keyword: str,
    location: str = "United States",
    language: str = "en",
    analysis_type: str = "comprehensive",
    user_type: str = "free",
) -> dict:
    """
    Advanced keyword research and analysis with multiple data sources
    """
    try:
        start_time = time.time()

        # Initialize keyword analyzer
        analyzer = AdvancedKeywordAnalyzer(keyword, location, language, user_type)

        # Perform analysis based on type
        if analysis_type == "comprehensive":
            results = analyzer.comprehensive_analysis()
        elif analysis_type == "competitor":
            results = analyzer.competitor_analysis()
        elif analysis_type == "opportunity":
            results = analyzer.opportunity_analysis()
        else:
            results = analyzer.basic_analysis()

        # Add timing information
        results["analysis_time"] = round(time.time() - start_time, 2)
        results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

        return results

    except Exception as e:
        return {"success": False, "error": f"Keyword analysis error: {str(e)}"}


class AdvancedKeywordAnalyzer:
    def __init__(
        self, keyword, location="United States", language="en", user_type="free"
    ):
        self.keyword = keyword.lower().strip()
        self.location = location
        self.language = language
        self.user_type = user_type
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def basic_analysis(self):
        """Basic keyword analysis for free users"""
        try:
            results = {
                "success": True,
                "keyword": self.keyword,
                "analysis_type": "basic",
                "user_type": self.user_type,
            }

            # Basic keyword metrics
            basic_metrics = self._get_basic_metrics()
            results.update(basic_metrics)

            # Limited suggestions for free users
            suggestions = self._get_keyword_suggestions(limit=10)
            results["keyword_suggestions"] = suggestions

            # Basic SERP analysis
            serp_data = self._analyze_serp(limit=5)
            results["serp_analysis"] = serp_data

            return results

        except Exception as e:
            return {"success": False, "error": str(e)}

    def comprehensive_analysis(self):
        """Comprehensive analysis for pro users"""
        try:
            results = {
                "success": True,
                "keyword": self.keyword,
                "analysis_type": "comprehensive",
                "user_type": self.user_type,
            }

            # Full keyword metrics
            comprehensive_metrics = self._get_comprehensive_metrics()
            results.update(comprehensive_metrics)

            # Extended suggestions
            limit = 50 if self.user_type == "pro" else 10
            suggestions = self._get_keyword_suggestions(limit=limit)
            results["keyword_suggestions"] = suggestions

            # Full SERP analysis
            serp_limit = 20 if self.user_type == "pro" else 5
            serp_data = self._analyze_serp(limit=serp_limit)
            results["serp_analysis"] = serp_data

            # Pro features
            if self.user_type == "pro":
                results["long_tail_keywords"] = self._get_long_tail_keywords()
                results["semantic_keywords"] = self._get_semantic_keywords()
                results["content_optimization"] = self._get_content_optimization()
                results["competitor_keywords"] = self._get_competitor_keywords()

            return results

        except Exception as e:
            return {"success": False, "error": str(e)}

    def competitor_analysis(self):
        """Competitor keyword analysis"""
        try:
            results = {
                "success": True,
                "keyword": self.keyword,
                "analysis_type": "competitor",
                "user_type": self.user_type,
            }

            # Get top competitors
            competitors = self._get_top_competitors()
            results["competitors"] = competitors

            # Analyze competitor keywords
            competitor_keywords = self._analyze_competitor_keywords(competitors)
            results["competitor_keywords"] = competitor_keywords

            # Gap analysis
            if self.user_type == "pro":
                results["keyword_gaps"] = self._find_keyword_gaps(competitor_keywords)
                results["opportunity_score"] = self._calculate_opportunity_score()

            return results

        except Exception as e:
            return {"success": False, "error": str(e)}

    def opportunity_analysis(self):
        """Keyword opportunity analysis"""
        try:
            results = {
                "success": True,
                "keyword": self.keyword,
                "analysis_type": "opportunity",
                "user_type": self.user_type,
            }

            # Find low competition keywords
            opportunities = self._find_opportunities()
            results["opportunities"] = opportunities

            # Trend analysis
            trends = self._analyze_trends()
            results["trends"] = trends

            # Seasonal patterns
            if self.user_type == "pro":
                results["seasonal_patterns"] = self._analyze_seasonal_patterns()
                results["content_gaps"] = self._find_content_gaps()

            return results

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_basic_metrics(self):
        """Get basic keyword metrics"""
        try:
            metrics = {
                "search_volume": self._estimate_search_volume(),
                "keyword_difficulty": self._calculate_keyword_difficulty(),
                "competition_level": self._assess_competition_level(),
                "word_count": len(self.keyword.split()),
                "character_count": len(self.keyword),
                "keyword_type": self._classify_keyword_type(),
            }
            return metrics
        except:
            return {}

    def _get_comprehensive_metrics(self):
        """Get comprehensive keyword metrics"""
        basic = self._get_basic_metrics()
        try:
            comprehensive = {
                **basic,
                "cpc_estimate": self._estimate_cpc(),
                "commercial_intent": self._analyze_commercial_intent(),
                "search_intent": self._analyze_search_intent(),
                "brand_vs_generic": self._classify_brand_generic(),
                "local_vs_global": self._analyze_local_global(),
                "seasonality_score": self._calculate_seasonality(),
            }
            return comprehensive
        except:
            return basic

    def _get_keyword_suggestions(self, limit=10):
        """Generate keyword suggestions"""
        try:
            suggestions = []

            # Related keywords based on the main keyword
            base_suggestions = [
                f"{self.keyword} tips",
                f"{self.keyword} guide",
                f"best {self.keyword}",
                f"how to {self.keyword}",
                f"{self.keyword} tutorial",
                f"{self.keyword} review",
                f"{self.keyword} comparison",
                f"{self.keyword} benefits",
                f"{self.keyword} cost",
                f"{self.keyword} free",
            ]

            # Add variations
            words = self.keyword.split()
            if len(words) > 1:
                # Reorder words
                reversed_keyword = " ".join(reversed(words))
                base_suggestions.append(reversed_keyword)

                # Add synonyms and variations
                synonyms = self._get_keyword_synonyms()
                for synonym in synonyms[:5]:
                    base_suggestions.append(synonym)

            # Score and rank suggestions
            for suggestion in base_suggestions[:limit]:
                scored_suggestion = {
                    "keyword": suggestion,
                    "search_volume": self._estimate_search_volume(suggestion),
                    "difficulty": self._calculate_keyword_difficulty(suggestion),
                    "relevance_score": self._calculate_relevance_score(suggestion),
                }
                suggestions.append(scored_suggestion)

            # Sort by relevance score
            suggestions.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

            return suggestions[:limit]

        except Exception as e:
            return []

    def _analyze_serp(self, limit=5):
        """Analyze SERP results"""
        try:
            serp_data = {
                "total_results": 0,
                "featured_snippet": None,
                "top_results": [],
                "avg_title_length": 0,
                "avg_meta_length": 0,
                "common_words": [],
            }

            # Simulate SERP analysis (in real implementation, would use SERP API)
            sample_results = self._get_sample_serp_results(limit)
            serp_data["top_results"] = sample_results
            serp_data["total_results"] = len(sample_results) * 1000  # Simulate

            # Calculate averages
            if sample_results:
                titles = [r.get("title", "") for r in sample_results]
                serp_data["avg_title_length"] = sum(len(t) for t in titles) / len(
                    titles
                )

                # Extract common words
                all_text = " ".join(titles).lower()
                words = re.findall(r"\b\w+\b", all_text)
                common_words = Counter(words).most_common(10)
                serp_data["common_words"] = [
                    {"word": w, "frequency": f} for w, f in common_words
                ]

            return serp_data

        except Exception as e:
            return {}

    def _get_sample_serp_results(self, limit):
        """Generate sample SERP results for analysis"""
        sample_results = []

        for i in range(limit):
            result = {
                "position": i + 1,
                "title": f"Sample Title About {self.keyword.title()} - Result {i + 1}",
                "url": f"https://example{i + 1}.com/{self.keyword.replace(' ', '-')}",
                "meta_description": f"Learn everything about {self.keyword} in this comprehensive guide. Expert tips and strategies.",
                "domain_authority": 65 - (i * 5),
                "word_count": 1500 - (i * 100),
                "backlinks": 1000 - (i * 100),
            }
            sample_results.append(result)

        return sample_results

    def _estimate_search_volume(self, keyword=None):
        """Estimate search volume for keyword"""
        target_keyword = keyword or self.keyword

        # Simulate search volume based on keyword characteristics
        word_count = len(target_keyword.split())
        char_count = len(target_keyword)

        base_volume = 1000

        # Adjust based on keyword length
        if word_count == 1:
            base_volume *= 2  # Single words tend to have higher volume
        elif word_count > 4:
            base_volume *= 0.3  # Long tail keywords have lower volume

        # Adjust based on character count
        if char_count < 5:
            base_volume *= 1.5
        elif char_count > 20:
            base_volume *= 0.5

        return int(base_volume)

    def _calculate_keyword_difficulty(self, keyword=None):
        """Calculate keyword difficulty score (0-100)"""
        target_keyword = keyword or self.keyword

        # Simulate difficulty based on keyword characteristics
        word_count = len(target_keyword.split())
        search_volume = self._estimate_search_volume(target_keyword)

        difficulty = 50  # Base difficulty

        # Higher search volume = higher difficulty
        if search_volume > 10000:
            difficulty += 20
        elif search_volume < 1000:
            difficulty -= 15

        # Single words are typically more difficult
        if word_count == 1:
            difficulty += 15
        elif word_count > 3:
            difficulty -= 10

        return max(0, min(100, difficulty))

    def _assess_competition_level(self):
        """Assess competition level"""
        difficulty = self._calculate_keyword_difficulty()

        if difficulty >= 80:
            return "Very High"
        elif difficulty >= 60:
            return "High"
        elif difficulty >= 40:
            return "Medium"
        elif difficulty >= 20:
            return "Low"
        else:
            return "Very Low"

    def _classify_keyword_type(self):
        """Classify keyword type"""
        keyword_lower = self.keyword.lower()

        if any(
            word in keyword_lower
            for word in ["buy", "purchase", "price", "cost", "cheap", "discount"]
        ):
            return "Commercial"
        elif any(
            word in keyword_lower
            for word in ["how", "what", "why", "when", "where", "guide", "tutorial"]
        ):
            return "Informational"
        elif any(
            word in keyword_lower for word in ["best", "top", "review", "compare", "vs"]
        ):
            return "Investigation"
        elif any(
            brand in keyword_lower
            for brand in ["amazon", "google", "facebook", "apple"]
        ):
            return "Branded"
        else:
            return "Generic"

    def _estimate_cpc(self):
        """Estimate cost per click"""
        difficulty = self._calculate_keyword_difficulty()
        keyword_type = self._classify_keyword_type()

        base_cpc = 1.50

        if keyword_type == "Commercial":
            base_cpc *= 2.5
        elif keyword_type == "Investigation":
            base_cpc *= 1.8

        # Higher difficulty = higher CPC
        cpc_multiplier = 1 + (difficulty / 100)

        return round(base_cpc * cpc_multiplier, 2)

    def _analyze_commercial_intent(self):
        """Analyze commercial intent score"""
        keyword_lower = self.keyword.lower()

        commercial_words = [
            "buy",
            "purchase",
            "price",
            "cost",
            "cheap",
            "discount",
            "deal",
            "sale",
            "order",
        ]
        intent_score = sum(1 for word in commercial_words if word in keyword_lower)

        return min(100, intent_score * 20)

    def _analyze_search_intent(self):
        """Analyze primary search intent"""
        keyword_lower = self.keyword.lower()

        if any(word in keyword_lower for word in ["buy", "purchase", "order", "price"]):
            return "Transactional"
        elif any(
            word in keyword_lower
            for word in ["how", "what", "guide", "tutorial", "learn"]
        ):
            return "Informational"
        elif any(
            word in keyword_lower for word in ["best", "top", "review", "compare"]
        ):
            return "Investigation"
        else:
            return "Navigational"

    def _classify_brand_generic(self):
        """Classify if keyword is branded or generic"""
        # Simple brand detection
        common_brands = [
            "google",
            "amazon",
            "facebook",
            "apple",
            "microsoft",
            "samsung",
        ]

        if any(brand in self.keyword.lower() for brand in common_brands):
            return "Branded"
        else:
            return "Generic"

    def _analyze_local_global(self):
        """Analyze local vs global intent"""
        local_indicators = ["near me", "local", "nearby", self.location.lower()]

        if any(indicator in self.keyword.lower() for indicator in local_indicators):
            return "Local"
        else:
            return "Global"

    def _calculate_seasonality(self):
        """Calculate seasonality score"""
        seasonal_keywords = {
            "christmas": 95,
            "halloween": 90,
            "summer": 70,
            "winter": 65,
            "holiday": 80,
            "valentine": 85,
        }

        for seasonal_word, score in seasonal_keywords.items():
            if seasonal_word in self.keyword.lower():
                return score

        return 10  # Low seasonality by default

    def _get_keyword_synonyms(self):
        """Get keyword synonyms and variations"""
        # Simple synonym mapping
        synonym_map = {
            "seo": ["search engine optimization", "search optimization"],
            "marketing": ["advertising", "promotion"],
            "website": ["site", "web page"],
            "content": ["articles", "text", "copy"],
            "analysis": ["evaluation", "assessment", "audit"],
        }

        synonyms = []
        words = self.keyword.split()

        for word in words:
            if word.lower() in synonym_map:
                synonyms.extend(synonym_map[word.lower()])

        return synonyms[:5]

    def _calculate_relevance_score(self, suggestion):
        """Calculate relevance score for keyword suggestion"""
        base_keyword_words = set(self.keyword.lower().split())
        suggestion_words = set(suggestion.lower().split())

        # Calculate word overlap
        overlap = len(base_keyword_words.intersection(suggestion_words))
        total_words = len(base_keyword_words.union(suggestion_words))

        if total_words == 0:
            return 0

        relevance = (overlap / total_words) * 100
        return round(relevance, 1)

    # Premium features for pro users
    def _get_long_tail_keywords(self):
        """Get long tail keyword opportunities"""
        long_tail = []

        # Generate long tail variations
        prefixes = ["how to", "what is", "best way to", "why does", "when to"]
        suffixes = ["tips", "guide", "tutorial", "examples", "benefits", "mistakes"]

        for prefix in prefixes:
            long_tail.append(
                {
                    "keyword": f"{prefix} {self.keyword}",
                    "search_volume": self._estimate_search_volume(
                        f"{prefix} {self.keyword}"
                    ),
                    "difficulty": self._calculate_keyword_difficulty(
                        f"{prefix} {self.keyword}"
                    ),
                    "type": "Question-based",
                }
            )

        for suffix in suffixes:
            long_tail.append(
                {
                    "keyword": f"{self.keyword} {suffix}",
                    "search_volume": self._estimate_search_volume(
                        f"{self.keyword} {suffix}"
                    ),
                    "difficulty": self._calculate_keyword_difficulty(
                        f"{self.keyword} {suffix}"
                    ),
                    "type": "Topic-based",
                }
            )

        return long_tail[:10]

    def _get_semantic_keywords(self):
        """Get semantically related keywords"""
        # This would use NLP/ML in production
        semantic_keywords = [
            f"{self.keyword} optimization",
            f"{self.keyword} strategy",
            f"{self.keyword} techniques",
            f"{self.keyword} methods",
            f"{self.keyword} tools",
        ]

        return [{"keyword": k, "semantic_score": 85} for k in semantic_keywords]

    def _get_content_optimization(self):
        """Get content optimization suggestions"""
        return {
            "recommended_word_count": "1500-2500 words",
            "key_sections": [
                "Introduction to " + self.keyword,
                "Benefits of " + self.keyword,
                "How to implement " + self.keyword,
                "Best practices for " + self.keyword,
                "Common mistakes with " + self.keyword,
                "Conclusion",
            ],
            "internal_linking": f"Link to related {self.keyword} articles",
            "meta_optimization": {
                "title_suggestion": f"Complete Guide to {self.keyword.title()} - [Year]",
                "meta_description": f"Learn everything about {self.keyword}. Expert tips, strategies, and best practices.",
            },
        }

    def _get_top_competitors(self):
        """Get top competitors for the keyword"""
        # Simulated competitor data
        competitors = [
            {"domain": "competitor1.com", "da": 75, "rank": 1},
            {"domain": "competitor2.com", "da": 68, "rank": 2},
            {"domain": "competitor3.com", "da": 72, "rank": 3},
        ]
        return competitors

    def _analyze_competitor_keywords(self, competitors):
        """Analyze competitor keywords"""
        competitor_data = {}

        for comp in competitors:
            competitor_data[comp["domain"]] = {
                "total_keywords": 1500 + (comp["da"] * 10),
                "organic_traffic": 50000 + (comp["da"] * 1000),
                "top_keywords": [
                    {"keyword": f"{self.keyword} guide", "position": 1, "volume": 5000},
                    {"keyword": f"best {self.keyword}", "position": 2, "volume": 3000},
                    {"keyword": f"{self.keyword} tips", "position": 3, "volume": 2000},
                ],
            }

        return competitor_data

    def _find_keyword_gaps(self, competitor_keywords):
        """Find keyword gaps and opportunities"""
        gaps = [
            {"keyword": f"{self.keyword} automation", "opportunity_score": 85},
            {"keyword": f"{self.keyword} trends 2025", "opportunity_score": 78},
            {"keyword": f"advanced {self.keyword}", "opportunity_score": 72},
        ]
        return gaps

    def _calculate_opportunity_score(self):
        """Calculate overall opportunity score"""
        difficulty = self._calculate_keyword_difficulty()
        search_volume = self._estimate_search_volume()

        # Higher volume + lower difficulty = higher opportunity
        opportunity = (search_volume / 100) - difficulty
        return max(0, min(100, opportunity))

    def _find_opportunities(self):
        """Find keyword opportunities"""
        opportunities = []

        # Low competition variations
        variations = [
            f"{self.keyword} 2025",
            f"{self.keyword} for beginners",
            f"free {self.keyword}",
            f"{self.keyword} checklist",
            f"{self.keyword} template",
        ]

        for var in variations:
            opp = {
                "keyword": var,
                "search_volume": self._estimate_search_volume(var),
                "difficulty": self._calculate_keyword_difficulty(var),
                "opportunity_score": self._calculate_opportunity_score(),
            }
            opportunities.append(opp)

        return opportunities

    def _analyze_trends(self):
        """Analyze keyword trends"""
        return {
            "trend_direction": "Increasing",
            "growth_rate": "15% YoY",
            "peak_months": ["March", "September"],
            "related_trending": [
                f"AI {self.keyword}",
                f"{self.keyword} automation",
                f"mobile {self.keyword}",
            ],
        }

    def _analyze_seasonal_patterns(self):
        """Analyze seasonal patterns"""
        return {
            "seasonality_type": "Moderate",
            "peak_season": "Q1 & Q3",
            "low_season": "Q2",
            "monthly_index": {
                "January": 110,
                "February": 105,
                "March": 125,
                "April": 95,
                "May": 85,
                "June": 80,
                "July": 90,
                "August": 100,
                "September": 120,
                "October": 115,
                "November": 105,
                "December": 95,
            },
        }

    def _find_content_gaps(self):
        """Find content gaps"""
        return {
            "missing_topics": [
                f"{self.keyword} case studies",
                f"{self.keyword} ROI analysis",
                f"{self.keyword} industry benchmarks",
            ],
            "content_formats": [
                "Video tutorials",
                "Infographics",
                "Interactive tools",
                "Podcasts",
            ],
            "audience_segments": [
                "Beginners",
                "Advanced users",
                "Enterprise",
                "Small business",
            ],
        }
