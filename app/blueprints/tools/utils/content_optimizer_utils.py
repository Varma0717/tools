import re
import math
import time
from collections import Counter, defaultdict
from textstat import (
    flesch_reading_ease,
    flesch_kincaid_grade,
    coleman_liau_index,
    automated_readability_index,
)
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")


def analyze_content_seo(
    content: str,
    target_keywords: str = "",
    analysis_type: str = "standard",
    user_type: str = "free",
) -> dict:
    """
    Comprehensive content SEO analysis
    """
    try:
        start_time = time.time()

        # Initialize content analyzer
        analyzer = ContentSEOAnalyzer(content, target_keywords, user_type)

        # Perform analysis based on type
        if analysis_type == "comprehensive":
            results = analyzer.comprehensive_analysis()
        elif analysis_type == "quick":
            results = analyzer.quick_analysis()
        elif analysis_type == "detailed":
            results = analyzer.detailed_analysis()
        else:
            results = analyzer.standard_analysis()

        # Add timing information
        results["analysis_time"] = round(time.time() - start_time, 2)
        results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

        return results

    except Exception as e:
        return {"success": False, "error": f"Content analysis error: {str(e)}"}


def get_improvement_suggestions(
    content: str,
    target_keywords: str = "",
    content_type: str = "blog",
    user_type: str = "free",
) -> dict:
    """
    Get content improvement suggestions
    """
    try:
        analyzer = ContentSEOAnalyzer(content, target_keywords, user_type)
        suggestions = analyzer.get_improvement_suggestions(content_type)

        return {
            "success": True,
            "suggestions": suggestions,
            "content_type": content_type,
            "user_type": user_type,
        }

    except Exception as e:
        return {"success": False, "error": f"Suggestions error: {str(e)}"}


def analyze_readability(content: str, user_type: str = "free") -> dict:
    """
    Analyze content readability
    """
    try:
        analyzer = ContentSEOAnalyzer(content, "", user_type)
        readability = analyzer.analyze_readability()

        return {"success": True, "readability": readability, "user_type": user_type}

    except Exception as e:
        return {"success": False, "error": f"Readability error: {str(e)}"}


class ContentSEOAnalyzer:
    def __init__(self, content, target_keywords="", user_type="free"):
        self.content = content.strip()
        self.target_keywords = (
            [kw.strip().lower() for kw in target_keywords.split(",") if kw.strip()]
            if target_keywords
            else []
        )
        self.user_type = user_type

        # Basic text processing
        self.sentences = sent_tokenize(self.content)
        self.words = word_tokenize(self.content.lower())
        self.word_count = len([w for w in self.words if w.isalpha()])
        self.sentence_count = len(self.sentences)
        self.paragraph_count = len([p for p in self.content.split("\n\n") if p.strip()])

        # Stop words
        self.stop_words = set(stopwords.words("english"))

    def quick_analysis(self):
        """Quick content analysis"""
        try:
            results = {
                "success": True,
                "content_length": len(self.content),
                "word_count": self.word_count,
                "sentence_count": self.sentence_count,
                "paragraph_count": self.paragraph_count,
                "analysis_type": "quick",
                "user_type": self.user_type,
            }

            # Basic keyword analysis
            if self.target_keywords:
                results["keyword_analysis"] = self._basic_keyword_analysis()

            # Basic readability
            results["readability_score"] = self._basic_readability()

            return results

        except Exception as e:
            return {"success": False, "error": str(e)}

    def standard_analysis(self):
        """Standard content analysis"""
        try:
            results = {
                "success": True,
                "content_stats": self._get_content_statistics(),
                "keyword_analysis": self._analyze_keywords(),
                "readability": self._basic_readability(),
                "structure_analysis": self._analyze_structure(),
                "seo_score": 0,
                "analysis_type": "standard",
                "user_type": self.user_type,
            }

            # Calculate SEO score
            results["seo_score"] = self._calculate_seo_score(results)

            return results

        except Exception as e:
            return {"success": False, "error": str(e)}

    def comprehensive_analysis(self):
        """Comprehensive content analysis for pro users"""
        try:
            results = self.standard_analysis()

            # Add comprehensive features
            results["analysis_type"] = "comprehensive"
            results["advanced_readability"] = self._advanced_readability()
            results["semantic_analysis"] = self._semantic_analysis()
            results["competitor_insights"] = self._competitor_insights()
            results["content_gaps"] = self._identify_content_gaps()

            if self.user_type == "pro":
                results["advanced_suggestions"] = self._get_advanced_suggestions()
                results["content_optimization"] = (
                    self._get_optimization_recommendations()
                )

            return results

        except Exception as e:
            return {"success": False, "error": str(e)}

    def detailed_analysis(self):
        """Detailed analysis with deep insights"""
        try:
            results = self.comprehensive_analysis()

            # Add detailed features
            results["analysis_type"] = "detailed"
            results["sentiment_analysis"] = self._analyze_sentiment()
            results["topic_modeling"] = self._analyze_topics()
            results["engagement_prediction"] = self._predict_engagement()

            return results

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_content_statistics(self):
        """Get basic content statistics"""
        return {
            "character_count": len(self.content),
            "character_count_no_spaces": len(self.content.replace(" ", "")),
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "paragraph_count": self.paragraph_count,
            "average_words_per_sentence": round(
                self.word_count / max(self.sentence_count, 1), 1
            ),
            "average_sentences_per_paragraph": round(
                self.sentence_count / max(self.paragraph_count, 1), 1
            ),
            "reading_time_minutes": math.ceil(self.word_count / 200),  # 200 WPM average
        }

    def _basic_keyword_analysis(self):
        """Basic keyword analysis"""
        if not self.target_keywords:
            return {"message": "No target keywords provided"}

        content_lower = self.content.lower()
        keyword_data = {}

        for keyword in self.target_keywords:
            count = content_lower.count(keyword.lower())
            density = (count / max(self.word_count, 1)) * 100

            keyword_data[keyword] = {
                "count": count,
                "density": round(density, 2),
                "status": (
                    "good"
                    if 0.5 <= density <= 3.0
                    else "warning" if density > 3.0 else "low"
                ),
            }

        return keyword_data

    def _analyze_keywords(self):
        """Comprehensive keyword analysis"""
        results = {
            "target_keywords": {},
            "keyword_distribution": {},
            "keyword_placement": {},
            "related_keywords": [],
        }

        if self.target_keywords:
            content_lower = self.content.lower()

            for keyword in self.target_keywords:
                # Basic metrics
                count = content_lower.count(keyword.lower())
                density = (count / max(self.word_count, 1)) * 100

                # Placement analysis
                first_paragraph = self.content[:200].lower()
                last_paragraph = self.content[-200:].lower()

                placement = {
                    "in_first_paragraph": keyword.lower() in first_paragraph,
                    "in_last_paragraph": keyword.lower() in last_paragraph,
                    "in_headings": self._check_keyword_in_headings(keyword),
                    "positions": [
                        i
                        for i, word in enumerate(self.words)
                        if keyword.lower()
                        in " ".join(self.words[i : i + len(keyword.split())])
                    ],
                }

                results["target_keywords"][keyword] = {
                    "count": count,
                    "density": round(density, 2),
                    "placement": placement,
                    "status": self._get_keyword_status(density, placement),
                    "recommendations": self._get_keyword_recommendations(
                        density, placement
                    ),
                }

        # Analyze keyword distribution throughout content
        results["keyword_distribution"] = self._analyze_keyword_distribution()

        # Find related keywords
        results["related_keywords"] = self._find_related_keywords()

        return results

    def _basic_readability(self):
        """Basic readability analysis"""
        try:
            return {
                "flesch_score": round(flesch_reading_ease(self.content), 1),
                "grade_level": round(flesch_kincaid_grade(self.content), 1),
                "reading_difficulty": self._get_reading_difficulty(
                    flesch_reading_ease(self.content)
                ),
            }
        except:
            return {
                "flesch_score": 0,
                "grade_level": 12,
                "reading_difficulty": "Unable to calculate",
            }

    def _advanced_readability(self):
        """Advanced readability analysis"""
        try:
            flesch_score = flesch_reading_ease(self.content)
            fk_grade = flesch_kincaid_grade(self.content)
            coleman_liau = coleman_liau_index(self.content)
            ari = automated_readability_index(self.content)

            return {
                "flesch_reading_ease": round(flesch_score, 1),
                "flesch_kincaid_grade": round(fk_grade, 1),
                "coleman_liau_index": round(coleman_liau, 1),
                "automated_readability_index": round(ari, 1),
                "average_grade_level": round((fk_grade + coleman_liau + ari) / 3, 1),
                "reading_difficulty": self._get_reading_difficulty(flesch_score),
                "recommendations": self._get_readability_recommendations(
                    flesch_score, fk_grade
                ),
            }
        except Exception as e:
            return {"error": f"Readability calculation failed: {str(e)}"}

    def _analyze_structure(self):
        """Analyze content structure"""
        headings = self._extract_headings()

        return {
            "headings": headings,
            "heading_count": len(headings),
            "has_introduction": len(self.content[:300]) > 200,
            "has_conclusion": len(self.content[-300:]) > 200,
            "paragraph_lengths": [
                len(p.split()) for p in self.content.split("\n\n") if p.strip()
            ],
            "sentence_lengths": [len(s.split()) for s in self.sentences],
            "structure_score": self._calculate_structure_score(headings),
        }

    def _semantic_analysis(self):
        """Semantic analysis of content"""
        # Word frequency analysis
        words_no_stop = [
            w for w in self.words if w.isalpha() and w not in self.stop_words
        ]
        word_freq = Counter(words_no_stop)

        # POS tagging analysis
        try:
            pos_tags = pos_tag(word_tokenize(self.content))
            pos_freq = Counter([tag for word, tag in pos_tags])
        except:
            pos_freq = {}

        return {
            "top_words": dict(word_freq.most_common(10)),
            "unique_words": len(set(words_no_stop)),
            "lexical_diversity": round(
                len(set(words_no_stop)) / max(len(words_no_stop), 1), 3
            ),
            "pos_distribution": dict(pos_freq),
            "content_themes": self._extract_themes(word_freq),
        }

    def _competitor_insights(self):
        """Competitor content insights"""
        return {
            "suggested_content_length": self._suggest_content_length(),
            "benchmark_metrics": {
                "ideal_word_count": "1500-2500 words",
                "ideal_paragraph_count": "8-15 paragraphs",
                "ideal_heading_count": "5-10 headings",
                "ideal_reading_time": "7-12 minutes",
            },
            "content_gaps": [
                "Add more examples",
                "Include case studies",
                "Add data/statistics",
            ],
            "improvement_areas": self._identify_improvement_areas(),
        }

    def _identify_content_gaps(self):
        """Identify gaps in content"""
        gaps = []

        # Check for common content elements
        content_lower = self.content.lower()

        if "example" not in content_lower and "for instance" not in content_lower:
            gaps.append("Consider adding examples to illustrate your points")

        if not re.search(r"\d+%|\d+\.\d+%", self.content):
            gaps.append("Add statistics or data to support your claims")

        if "conclusion" not in content_lower and "summary" not in content_lower:
            gaps.append("Consider adding a clear conclusion or summary")

        if self.word_count < 300:
            gaps.append("Content is quite short - consider expanding key points")

        return gaps

    def _get_advanced_suggestions(self):
        """Get advanced content suggestions for pro users"""
        suggestions = []

        # Keyword suggestions
        if self.target_keywords:
            for keyword in self.target_keywords:
                density = (
                    self.content.lower().count(keyword.lower())
                    / max(self.word_count, 1)
                ) * 100
                if density < 0.5:
                    suggestions.append(
                        f"Increase usage of '{keyword}' (current density: {density:.2f}%)"
                    )
                elif density > 3.0:
                    suggestions.append(
                        f"Reduce usage of '{keyword}' to avoid keyword stuffing (current density: {density:.2f}%)"
                    )

        # Structure suggestions
        if self.paragraph_count < 3:
            suggestions.append(
                "Break content into more paragraphs for better readability"
            )

        if self.sentence_count > 0:
            avg_sentence_length = self.word_count / self.sentence_count
            if avg_sentence_length > 25:
                suggestions.append("Consider shorter sentences for better readability")

        # Content depth suggestions
        if self.word_count < 500:
            suggestions.append("Consider expanding content for better SEO performance")

        return suggestions

    def _get_optimization_recommendations(self):
        """Get detailed optimization recommendations"""
        recommendations = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
        }

        # High priority recommendations
        if self.word_count < 300:
            recommendations["high_priority"].append(
                "Expand content to at least 300 words"
            )

        if self.target_keywords:
            for keyword in self.target_keywords:
                if keyword.lower() not in self.content.lower():
                    recommendations["high_priority"].append(
                        f"Include target keyword '{keyword}' in content"
                    )

        # Medium priority recommendations
        if self.paragraph_count < 3:
            recommendations["medium_priority"].append(
                "Improve content structure with more paragraphs"
            )

        # Low priority recommendations
        try:
            flesch_score = flesch_reading_ease(self.content)
            if flesch_score < 30:
                recommendations["low_priority"].append(
                    "Improve readability by simplifying language"
                )
        except:
            pass

        return recommendations

    def _analyze_sentiment(self):
        """Basic sentiment analysis"""
        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "outstanding",
            "brilliant",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "horrible",
            "disappointing",
            "poor",
            "worst",
            "hate",
        ]

        content_words = [w.lower() for w in self.words if w.isalpha()]

        positive_count = sum(1 for word in content_words if word in positive_words)
        negative_count = sum(1 for word in content_words if word in negative_words)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "sentiment_score": round(
                (positive_count - negative_count) / max(len(content_words), 1), 3
            ),
        }

    def _analyze_topics(self):
        """Basic topic analysis"""
        # Extract important words (excluding stop words)
        important_words = [
            w
            for w in self.words
            if w.isalpha() and len(w) > 3 and w not in self.stop_words
        ]
        word_freq = Counter(important_words)

        return {
            "main_topics": [word for word, count in word_freq.most_common(5)],
            "topic_distribution": dict(word_freq.most_common(10)),
            "content_focus": (
                "well-focused" if len(word_freq.most_common(3)) > 0 else "needs focus"
            ),
        }

    def _predict_engagement(self):
        """Predict content engagement potential"""
        engagement_score = 50  # Base score

        # Length factor
        if 800 <= self.word_count <= 2000:
            engagement_score += 20
        elif self.word_count < 300:
            engagement_score -= 20

        # Readability factor
        try:
            flesch_score = flesch_reading_ease(self.content)
            if 60 <= flesch_score <= 80:
                engagement_score += 15
            elif flesch_score < 30:
                engagement_score -= 15
        except:
            pass

        # Structure factor
        if 3 <= self.paragraph_count <= 10:
            engagement_score += 10

        # Question factor (engagement indicator)
        question_count = self.content.count("?")
        if question_count > 0:
            engagement_score += min(question_count * 5, 15)

        return {
            "engagement_score": max(0, min(100, engagement_score)),
            "prediction": (
                "high"
                if engagement_score >= 80
                else "medium" if engagement_score >= 60 else "low"
            ),
            "factors": {
                "content_length": (
                    "optimal" if 800 <= self.word_count <= 2000 else "suboptimal"
                ),
                "readability": (
                    "good"
                    if 60 <= flesch_reading_ease(self.content) <= 80
                    else "needs improvement"
                ),
                "structure": (
                    "good" if 3 <= self.paragraph_count <= 10 else "needs improvement"
                ),
                "interactivity": (
                    "good" if question_count > 0 else "could add questions"
                ),
            },
        }

    def analyze_readability(self):
        """Comprehensive readability analysis"""
        if self.user_type == "pro":
            return self._advanced_readability()
        else:
            return self._basic_readability()

    def get_improvement_suggestions(self, content_type="blog"):
        """Get content improvement suggestions based on type"""
        suggestions = {"general": [], "seo": [], "readability": [], "engagement": []}

        # General suggestions
        if self.word_count < 300:
            suggestions["general"].append(
                "Expand your content to at least 300 words for better SEO"
            )

        if self.paragraph_count < 3:
            suggestions["general"].append("Break your content into more paragraphs")

        # SEO suggestions
        if self.target_keywords:
            for keyword in self.target_keywords:
                density = (
                    self.content.lower().count(keyword.lower())
                    / max(self.word_count, 1)
                ) * 100
                if density < 0.5:
                    suggestions["seo"].append(
                        f"Include '{keyword}' more frequently (current density: {density:.1f}%)"
                    )

        # Readability suggestions
        try:
            flesch_score = flesch_reading_ease(self.content)
            if flesch_score < 50:
                suggestions["readability"].append(
                    "Simplify language and use shorter sentences"
                )
        except:
            pass

        # Engagement suggestions
        if "?" not in self.content:
            suggestions["engagement"].append("Add questions to engage readers")

        if content_type == "blog" and self.word_count < 800:
            suggestions["engagement"].append(
                "Consider expanding to 800+ words for better blog performance"
            )

        return suggestions

    # Helper methods
    def _check_keyword_in_headings(self, keyword):
        """Check if keyword appears in headings"""
        headings = self._extract_headings()
        return any(keyword.lower() in heading.lower() for heading in headings)

    def _extract_headings(self):
        """Extract headings from content"""
        # Simple regex to find markdown-style headings
        headings = re.findall(r"^#+\s+(.+)$", self.content, re.MULTILINE)
        return headings

    def _get_keyword_status(self, density, placement):
        """Determine keyword status"""
        if density < 0.5:
            return "underused"
        elif density > 3.0:
            return "overused"
        elif placement["in_first_paragraph"] and placement["in_headings"]:
            return "optimal"
        else:
            return "good"

    def _get_keyword_recommendations(self, density, placement):
        """Get keyword-specific recommendations"""
        recommendations = []

        if density < 0.5:
            recommendations.append("Increase keyword usage")
        elif density > 3.0:
            recommendations.append("Reduce keyword usage to avoid stuffing")

        if not placement["in_first_paragraph"]:
            recommendations.append("Include keyword in first paragraph")

        if not placement["in_headings"]:
            recommendations.append("Include keyword in headings")

        return recommendations

    def _analyze_keyword_distribution(self):
        """Analyze how keywords are distributed throughout content"""
        if not self.target_keywords:
            return {}

        # Divide content into sections
        content_length = len(self.content)
        sections = {
            "beginning": self.content[: content_length // 3],
            "middle": self.content[content_length // 3 : 2 * content_length // 3],
            "end": self.content[2 * content_length // 3 :],
        }

        distribution = {}
        for keyword in self.target_keywords:
            distribution[keyword] = {
                section: sections[section].lower().count(keyword.lower())
                for section in sections
            }

        return distribution

    def _find_related_keywords(self):
        """Find related keywords in content"""
        # Simple approach: find frequent words that might be related
        words_no_stop = [
            w
            for w in self.words
            if w.isalpha() and len(w) > 3 and w not in self.stop_words
        ]
        word_freq = Counter(words_no_stop)

        # Return top frequent words as potential related keywords
        return [word for word, count in word_freq.most_common(10) if count >= 2]

    def _get_reading_difficulty(self, flesch_score):
        """Convert Flesch score to reading difficulty"""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"

    def _get_readability_recommendations(self, flesch_score, grade_level):
        """Get readability improvement recommendations"""
        recommendations = []

        if flesch_score < 50:
            recommendations.append("Use simpler words and shorter sentences")

        if grade_level > 12:
            recommendations.append(
                "Lower the reading level for broader audience appeal"
            )

        if self.sentence_count > 0:
            avg_sentence_length = self.word_count / self.sentence_count
            if avg_sentence_length > 20:
                recommendations.append(
                    "Use shorter sentences (aim for 15-20 words per sentence)"
                )

        return recommendations

    def _calculate_structure_score(self, headings):
        """Calculate content structure score"""
        score = 50  # Base score

        # Heading structure
        if len(headings) > 0:
            score += 20
        if len(headings) >= 3:
            score += 10

        # Paragraph structure
        if 3 <= self.paragraph_count <= 15:
            score += 15

        # Sentence variety
        if self.sentence_count > 0:
            avg_sentence_length = self.word_count / self.sentence_count
            if 15 <= avg_sentence_length <= 25:
                score += 5

        return min(100, score)

    def _extract_themes(self, word_freq):
        """Extract main themes from word frequency"""
        return [word for word, count in word_freq.most_common(5) if count >= 3]

    def _suggest_content_length(self):
        """Suggest optimal content length"""
        if self.word_count < 500:
            return "500-800 words (current: short)"
        elif self.word_count < 1000:
            return "1000-1500 words (current: medium)"
        elif self.word_count < 2000:
            return "Optimal length (current: good)"
        else:
            return "Consider breaking into multiple pieces (current: very long)"

    def _identify_improvement_areas(self):
        """Identify specific areas for improvement"""
        areas = []

        if self.word_count < 500:
            areas.append("Content depth")

        if self.paragraph_count < 3:
            areas.append("Content structure")

        try:
            flesch_score = flesch_reading_ease(self.content)
            if flesch_score < 50:
                areas.append("Readability")
        except:
            pass

        if not self.target_keywords:
            areas.append("Keyword optimization")

        return areas

    def _calculate_seo_score(self, analysis_data):
        """Calculate overall SEO score"""
        score = 0
        max_score = 100

        # Content length (20 points)
        if 500 <= self.word_count <= 2000:
            score += 20
        elif 300 <= self.word_count < 500:
            score += 15
        elif self.word_count >= 2000:
            score += 10
        else:
            score += 5

        # Keyword optimization (25 points)
        if self.target_keywords:
            keyword_score = 0
            for keyword in self.target_keywords:
                density = (
                    self.content.lower().count(keyword.lower())
                    / max(self.word_count, 1)
                ) * 100
                if 0.5 <= density <= 3.0:
                    keyword_score += 25 / len(self.target_keywords)
                elif 0.1 <= density < 0.5 or 3.0 < density <= 5.0:
                    keyword_score += 15 / len(self.target_keywords)
                else:
                    keyword_score += 5 / len(self.target_keywords)
            score += keyword_score
        else:
            score += 5  # Minimal score for no keywords

        # Readability (20 points)
        try:
            flesch_score = flesch_reading_ease(self.content)
            if 60 <= flesch_score <= 80:
                score += 20
            elif 50 <= flesch_score < 60 or 80 < flesch_score <= 90:
                score += 15
            else:
                score += 10
        except:
            score += 10

        # Structure (20 points)
        structure_score = analysis_data.get("structure_analysis", {}).get(
            "structure_score", 50
        )
        score += (structure_score / 100) * 20

        # Content quality (15 points)
        if self.paragraph_count >= 3:
            score += 8
        if self.sentence_count >= 5:
            score += 7

        return min(100, round(score))
