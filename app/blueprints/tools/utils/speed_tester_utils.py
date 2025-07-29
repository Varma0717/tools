"""
Website Speed Testing utilities for analyzing page performance and Core Web Vitals.
"""

import requests
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any, Optional


class SpeedTester:
    """Website speed testing and Core Web Vitals analyzer."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # Core Web Vitals thresholds
        self.cwv_thresholds = {
            "lcp": {
                "good": 2.5,
                "needs_improvement": 4.0,
            },  # Largest Contentful Paint (seconds)
            "fid": {
                "good": 100,
                "needs_improvement": 300,
            },  # First Input Delay (milliseconds)
            "cls": {"good": 0.1, "needs_improvement": 0.25},  # Cumulative Layout Shift
            "fcp": {
                "good": 1.8,
                "needs_improvement": 3.0,
            },  # First Contentful Paint (seconds)
            "ttfb": {
                "good": 0.8,
                "needs_improvement": 1.8,
            },  # Time to First Byte (seconds)
        }

    def analyze_speed(self, url: str) -> Dict[str, Any]:
        """Comprehensive speed analysis."""
        try:
            # Basic performance metrics
            performance_data = self._measure_basic_performance(url)

            # Page analysis
            page_analysis = self._analyze_page_structure(url)

            # Resource analysis
            resource_analysis = self._analyze_resources(url)

            # Generate overall score
            overall_score = self._calculate_speed_score(
                performance_data, page_analysis, resource_analysis
            )

            # Generate recommendations
            recommendations = self._generate_speed_recommendations(
                performance_data, page_analysis, resource_analysis
            )

            return {
                "performance_metrics": performance_data,
                "page_analysis": page_analysis,
                "resource_analysis": resource_analysis,
                "overall_score": overall_score,
                "recommendations": recommendations,
                "analysis_timestamp": time.time(),
            }

        except Exception as e:
            raise Exception(f"Speed analysis failed: {str(e)}")

    def analyze_core_web_vitals(self, url: str) -> Dict[str, Any]:
        """Analyze Core Web Vitals specifically."""
        try:
            # Measure basic performance for CWV estimation
            performance_data = self._measure_basic_performance(url)

            # Estimate Core Web Vitals based on measurable metrics
            cwv_estimates = self._estimate_core_web_vitals(url, performance_data)

            # CWV-specific recommendations
            cwv_recommendations = self._generate_cwv_recommendations(cwv_estimates)

            return {
                "core_web_vitals": cwv_estimates,
                "cwv_score": self._calculate_cwv_score(cwv_estimates),
                "recommendations": cwv_recommendations,
                "thresholds": self.cwv_thresholds,
                "analysis_timestamp": time.time(),
            }

        except Exception as e:
            raise Exception(f"Core Web Vitals analysis failed: {str(e)}")

    def get_performance_insights(self, url: str) -> Dict[str, Any]:
        """Get detailed performance insights and optimization opportunities."""
        try:
            # Comprehensive analysis
            speed_data = self.analyze_speed(url)
            cwv_data = self.analyze_core_web_vitals(url)

            # Additional insights
            technical_insights = self._analyze_technical_factors(url)
            optimization_opportunities = self._identify_optimization_opportunities(
                url, speed_data
            )

            # Competitive analysis (simulated)
            competitive_insights = self._generate_competitive_insights(
                speed_data["overall_score"]
            )

            return {
                "performance_summary": {
                    "speed_score": speed_data["overall_score"],
                    "cwv_score": cwv_data["cwv_score"],
                    "overall_grade": self._calculate_overall_grade(
                        speed_data["overall_score"], cwv_data["cwv_score"]
                    ),
                },
                "technical_insights": technical_insights,
                "optimization_opportunities": optimization_opportunities,
                "competitive_insights": competitive_insights,
                "detailed_metrics": {
                    "speed_analysis": speed_data,
                    "cwv_analysis": cwv_data,
                },
                "analysis_timestamp": time.time(),
            }

        except Exception as e:
            raise Exception(f"Performance insights failed: {str(e)}")

    def _measure_basic_performance(self, url: str) -> Dict[str, Any]:
        """Measure basic performance metrics."""
        try:
            # DNS lookup time simulation
            dns_start = time.time()
            parsed_url = urlparse(url)
            dns_time = (time.time() - dns_start) * 1000  # Convert to milliseconds

            # Full page load measurement
            start_time = time.time()
            response = self.session.get(url, timeout=30)
            load_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Response metrics
            response_size = len(response.content)
            response_headers = dict(response.headers)

            # Calculate TTFB (Time to First Byte)
            ttfb = response.elapsed.total_seconds() * 1000  # Convert to milliseconds

            return {
                "load_time_ms": round(load_time, 2),
                "ttfb_ms": round(ttfb, 2),
                "dns_time_ms": round(dns_time, 2),
                "response_size_bytes": response_size,
                "response_size_kb": round(response_size / 1024, 2),
                "status_code": response.status_code,
                "server": response_headers.get("server", "Unknown"),
                "content_encoding": response_headers.get("content-encoding"),
                "cache_control": response_headers.get("cache-control"),
                "content_type": response_headers.get("content-type"),
                "redirects": len(response.history),
            }

        except Exception as e:
            raise Exception(f"Performance measurement failed: {str(e)}")

    def _analyze_page_structure(self, url: str) -> Dict[str, Any]:
        """Analyze page structure for performance impact."""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")

            # Count different elements
            images = soup.find_all("img")
            scripts = soup.find_all("script")
            stylesheets = soup.find_all("link", rel="stylesheet")

            # Analyze image optimization
            image_analysis = self._analyze_images(images, url)

            # Analyze scripts
            script_analysis = self._analyze_scripts(scripts, url)

            # Analyze CSS
            css_analysis = self._analyze_css(stylesheets, url)

            # HTML structure analysis
            html_size = len(response.content)
            dom_elements = len(soup.find_all())

            return {
                "html_size_kb": round(html_size / 1024, 2),
                "dom_elements": dom_elements,
                "image_count": len(images),
                "script_count": len(scripts),
                "stylesheet_count": len(stylesheets),
                "image_analysis": image_analysis,
                "script_analysis": script_analysis,
                "css_analysis": css_analysis,
                "meta_viewport": bool(soup.find("meta", attrs={"name": "viewport"})),
                "has_h1": bool(soup.find("h1")),
                "title_length": len(soup.title.string) if soup.title else 0,
            }

        except Exception as e:
            raise Exception(f"Page structure analysis failed: {str(e)}")

    def _analyze_resources(self, url: str) -> Dict[str, Any]:
        """Analyze external resources and their impact."""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")

            # Find external resources
            external_scripts = []
            external_styles = []
            external_images = []

            base_domain = urlparse(url).netloc

            # Analyze scripts
            for script in soup.find_all("script", src=True):
                src = script.get("src")
                if src:
                    full_url = urljoin(url, src)
                    script_domain = urlparse(full_url).netloc
                    is_external = script_domain != base_domain

                    external_scripts.append(
                        {
                            "url": full_url,
                            "is_external": is_external,
                            "domain": script_domain,
                            "async": script.has_attr("async"),
                            "defer": script.has_attr("defer"),
                        }
                    )

            # Analyze stylesheets
            for link in soup.find_all("link", rel="stylesheet"):
                href = link.get("href")
                if href:
                    full_url = urljoin(url, href)
                    css_domain = urlparse(full_url).netloc
                    is_external = css_domain != base_domain

                    external_styles.append(
                        {
                            "url": full_url,
                            "is_external": is_external,
                            "domain": css_domain,
                            "media": link.get("media", "all"),
                        }
                    )

            # Count third-party domains
            third_party_domains = set()
            for script in external_scripts:
                if script["is_external"]:
                    third_party_domains.add(script["domain"])
            for style in external_styles:
                if style["is_external"]:
                    third_party_domains.add(style["domain"])

            return {
                "external_scripts": len(
                    [s for s in external_scripts if s["is_external"]]
                ),
                "external_stylesheets": len(
                    [s for s in external_styles if s["is_external"]]
                ),
                "third_party_domains": len(third_party_domains),
                "async_scripts": len([s for s in external_scripts if s["async"]]),
                "defer_scripts": len([s for s in external_scripts if s["defer"]]),
                "blocking_resources": len(
                    [s for s in external_scripts if not s["async"] and not s["defer"]]
                ),
                "total_external_requests": len(external_scripts) + len(external_styles),
            }

        except Exception as e:
            return {
                "external_scripts": 0,
                "external_stylesheets": 0,
                "third_party_domains": 0,
                "async_scripts": 0,
                "defer_scripts": 0,
                "blocking_resources": 0,
                "total_external_requests": 0,
                "analysis_error": str(e),
            }

    def _analyze_images(self, images: List, base_url: str) -> Dict[str, Any]:
        """Analyze image optimization."""
        try:
            total_images = len(images)
            images_with_alt = len([img for img in images if img.get("alt")])
            images_with_loading = len([img for img in images if img.get("loading")])
            lazy_loaded = len([img for img in images if img.get("loading") == "lazy"])

            # Check for modern formats (based on file extensions in src)
            webp_images = 0
            avif_images = 0
            large_images = 0

            for img in images[:10]:  # Sample first 10 images to avoid too many requests
                src = img.get("src")
                if src:
                    if ".webp" in src.lower():
                        webp_images += 1
                    elif ".avif" in src.lower():
                        avif_images += 1

            return {
                "total_images": total_images,
                "images_with_alt": images_with_alt,
                "alt_percentage": round(
                    (images_with_alt / total_images * 100) if total_images > 0 else 0, 1
                ),
                "lazy_loaded": lazy_loaded,
                "lazy_percentage": round(
                    (lazy_loaded / total_images * 100) if total_images > 0 else 0, 1
                ),
                "webp_images": webp_images,
                "avif_images": avif_images,
                "modern_format_percentage": round(
                    (
                        ((webp_images + avif_images) / min(10, total_images) * 100)
                        if total_images > 0
                        else 0
                    ),
                    1,
                ),
            }

        except Exception as e:
            return {"analysis_error": str(e)}

    def _analyze_scripts(self, scripts: List, base_url: str) -> Dict[str, Any]:
        """Analyze JavaScript optimization."""
        try:
            total_scripts = len(scripts)
            async_scripts = len([s for s in scripts if s.get("async")])
            defer_scripts = len([s for s in scripts if s.get("defer")])
            inline_scripts = len([s for s in scripts if not s.get("src")])

            return {
                "total_scripts": total_scripts,
                "async_scripts": async_scripts,
                "defer_scripts": defer_scripts,
                "inline_scripts": inline_scripts,
                "optimized_percentage": round(
                    (
                        ((async_scripts + defer_scripts) / total_scripts * 100)
                        if total_scripts > 0
                        else 0
                    ),
                    1,
                ),
            }

        except Exception as e:
            return {"analysis_error": str(e)}

    def _analyze_css(self, stylesheets: List, base_url: str) -> Dict[str, Any]:
        """Analyze CSS optimization."""
        try:
            total_css = len(stylesheets)
            critical_css = len(
                [
                    s
                    for s in stylesheets
                    if s.get("media") == "all" or not s.get("media")
                ]
            )

            return {
                "total_stylesheets": total_css,
                "critical_css": critical_css,
                "non_critical_css": total_css - critical_css,
            }

        except Exception as e:
            return {"analysis_error": str(e)}

    def _estimate_core_web_vitals(
        self, url: str, performance_data: Dict
    ) -> Dict[str, Any]:
        """Estimate Core Web Vitals based on measurable metrics."""
        try:
            # These are estimates based on available data
            # In a real implementation, you'd use tools like Lighthouse or PageSpeed Insights API

            load_time_s = performance_data["load_time_ms"] / 1000
            ttfb_s = performance_data["ttfb_ms"] / 1000

            # Estimate LCP (Largest Contentful Paint)
            # Usually 1.2-2x of load time for content-heavy pages
            estimated_lcp = min(load_time_s * 1.5, 10.0)

            # Estimate FCP (First Contentful Paint)
            # Usually occurs after TTFB + some rendering time
            estimated_fcp = ttfb_s + 0.5

            # Estimate CLS (Cumulative Layout Shift)
            # Lower score for pages with fewer external resources
            external_resources = performance_data.get("redirects", 0)
            estimated_cls = min(0.05 + (external_resources * 0.02), 0.5)

            # Estimate FID (First Input Delay)
            # Based on script load complexity
            estimated_fid = min(50 + (load_time_s * 20), 500)

            return {
                "lcp": {
                    "value": round(estimated_lcp, 2),
                    "unit": "seconds",
                    "status": self._get_cwv_status("lcp", estimated_lcp),
                    "description": "Largest Contentful Paint",
                },
                "fcp": {
                    "value": round(estimated_fcp, 2),
                    "unit": "seconds",
                    "status": self._get_cwv_status("fcp", estimated_fcp),
                    "description": "First Contentful Paint",
                },
                "cls": {
                    "value": round(estimated_cls, 3),
                    "unit": "score",
                    "status": self._get_cwv_status("cls", estimated_cls),
                    "description": "Cumulative Layout Shift",
                },
                "fid": {
                    "value": round(estimated_fid, 0),
                    "unit": "milliseconds",
                    "status": self._get_cwv_status("fid", estimated_fid),
                    "description": "First Input Delay",
                },
                "ttfb": {
                    "value": round(ttfb_s, 2),
                    "unit": "seconds",
                    "status": self._get_cwv_status("ttfb", ttfb_s),
                    "description": "Time to First Byte",
                },
            }

        except Exception as e:
            raise Exception(f"CWV estimation failed: {str(e)}")

    def _get_cwv_status(self, metric: str, value: float) -> str:
        """Get Core Web Vitals status (good/needs_improvement/poor)."""
        thresholds = self.cwv_thresholds.get(metric, {})

        if value <= thresholds.get("good", 0):
            return "good"
        elif value <= thresholds.get("needs_improvement", 0):
            return "needs_improvement"
        else:
            return "poor"

    def _calculate_speed_score(
        self, performance_data: Dict, page_analysis: Dict, resource_analysis: Dict
    ) -> int:
        """Calculate overall speed score (0-100)."""
        try:
            score = 100

            # Load time penalty (0-40 points)
            load_time_s = performance_data["load_time_ms"] / 1000
            if load_time_s > 3:
                score -= min(40, (load_time_s - 3) * 10)

            # TTFB penalty (0-20 points)
            ttfb_s = performance_data["ttfb_ms"] / 1000
            if ttfb_s > 1:
                score -= min(20, (ttfb_s - 1) * 20)

            # Resource optimization (0-20 points)
            if resource_analysis["blocking_resources"] > 3:
                score -= min(15, resource_analysis["blocking_resources"] * 2)

            # Page size penalty (0-15 points)
            if page_analysis["html_size_kb"] > 500:
                score -= min(15, (page_analysis["html_size_kb"] - 500) / 100)

            # External resources penalty (0-5 points)
            if resource_analysis["third_party_domains"] > 5:
                score -= min(5, resource_analysis["third_party_domains"] - 5)

            return max(0, min(100, round(score)))

        except Exception:
            return 50  # Default score if calculation fails

    def _calculate_cwv_score(self, cwv_data: Dict) -> int:
        """Calculate Core Web Vitals score (0-100)."""
        try:
            scores = []

            for metric, data in cwv_data.items():
                status = data["status"]
                if status == "good":
                    scores.append(100)
                elif status == "needs_improvement":
                    scores.append(70)
                else:  # poor
                    scores.append(30)

            return round(sum(scores) / len(scores)) if scores else 50

        except Exception:
            return 50

    def _calculate_overall_grade(self, speed_score: int, cwv_score: int) -> str:
        """Calculate overall performance grade."""
        overall_score = (speed_score + cwv_score) / 2

        if overall_score >= 90:
            return "A+"
        elif overall_score >= 80:
            return "A"
        elif overall_score >= 70:
            return "B"
        elif overall_score >= 60:
            return "C"
        elif overall_score >= 50:
            return "D"
        else:
            return "F"

    def _generate_speed_recommendations(
        self, performance_data: Dict, page_analysis: Dict, resource_analysis: Dict
    ) -> List[str]:
        """Generate speed optimization recommendations."""
        recommendations = []

        # Load time recommendations
        load_time_s = performance_data["load_time_ms"] / 1000
        if load_time_s > 3:
            recommendations.append(
                "Optimize page load time - consider enabling compression, optimizing images, and minimizing HTTP requests"
            )

        # TTFB recommendations
        ttfb_s = performance_data["ttfb_ms"] / 1000
        if ttfb_s > 1:
            recommendations.append(
                "Improve server response time - consider upgrading hosting, optimizing database queries, or using a CDN"
            )

        # Image optimization
        image_analysis = page_analysis.get("image_analysis", {})
        if image_analysis.get("total_images", 0) > 0:
            if image_analysis.get("lazy_percentage", 0) < 50:
                recommendations.append(
                    "Implement lazy loading for images to improve initial page load"
                )
            if image_analysis.get("modern_format_percentage", 0) < 50:
                recommendations.append(
                    "Use modern image formats like WebP or AVIF for better compression"
                )
            if image_analysis.get("alt_percentage", 0) < 90:
                recommendations.append(
                    "Add alt text to images for better accessibility and SEO"
                )

        # Script optimization
        if resource_analysis["blocking_resources"] > 2:
            recommendations.append(
                "Add async or defer attributes to non-critical JavaScript files"
            )

        # CSS optimization
        if page_analysis["stylesheet_count"] > 3:
            recommendations.append(
                "Minimize CSS files and consider inlining critical CSS"
            )

        # Third-party resources
        if resource_analysis["third_party_domains"] > 5:
            recommendations.append(
                "Reduce third-party scripts and consider self-hosting critical resources"
            )

        # Page size
        if page_analysis["html_size_kb"] > 500:
            recommendations.append(
                "Minimize HTML size by removing unnecessary code and comments"
            )

        # Caching
        if not performance_data.get("cache_control"):
            recommendations.append(
                "Implement proper caching headers to reduce repeat load times"
            )

        # Compression
        if not performance_data.get("content_encoding"):
            recommendations.append(
                "Enable Gzip or Brotli compression to reduce file sizes"
            )

        return recommendations[:8]  # Limit to top 8 recommendations

    def _generate_cwv_recommendations(self, cwv_data: Dict) -> List[str]:
        """Generate Core Web Vitals specific recommendations."""
        recommendations = []

        # LCP recommendations
        lcp_status = cwv_data.get("lcp", {}).get("status")
        if lcp_status in ["needs_improvement", "poor"]:
            recommendations.append(
                "Optimize Largest Contentful Paint by optimizing images, preloading key resources, and improving server response times"
            )

        # FCP recommendations
        fcp_status = cwv_data.get("fcp", {}).get("status")
        if fcp_status in ["needs_improvement", "poor"]:
            recommendations.append(
                "Improve First Contentful Paint by minimizing render-blocking resources and optimizing CSS delivery"
            )

        # CLS recommendations
        cls_status = cwv_data.get("cls", {}).get("status")
        if cls_status in ["needs_improvement", "poor"]:
            recommendations.append(
                "Reduce Cumulative Layout Shift by setting image dimensions, avoiding dynamically injected content, and using CSS transforms"
            )

        # FID recommendations
        fid_status = cwv_data.get("fid", {}).get("status")
        if fid_status in ["needs_improvement", "poor"]:
            recommendations.append(
                "Optimize First Input Delay by breaking up long-running JavaScript tasks and using web workers"
            )

        # TTFB recommendations
        ttfb_status = cwv_data.get("ttfb", {}).get("status")
        if ttfb_status in ["needs_improvement", "poor"]:
            recommendations.append(
                "Improve Time to First Byte with better hosting, CDN usage, and server optimization"
            )

        return recommendations

    def _analyze_technical_factors(self, url: str) -> Dict[str, Any]:
        """Analyze technical factors affecting performance."""
        try:
            response = self.session.get(url, timeout=30)
            headers = dict(response.headers)

            # HTTP/2 detection (simplified)
            http2_support = (
                "HTTP/2" in str(response.raw.version)
                if hasattr(response.raw, "version")
                else False
            )

            # Security headers
            security_headers = {
                "hsts": "strict-transport-security" in headers,
                "csp": "content-security-policy" in headers,
                "x_frame_options": "x-frame-options" in headers,
            }

            # Performance headers
            performance_headers = {
                "cache_control": headers.get("cache-control"),
                "expires": headers.get("expires"),
                "etag": headers.get("etag"),
                "last_modified": headers.get("last-modified"),
            }

            # Server information
            server_info = {
                "server": headers.get("server", "Unknown"),
                "powered_by": headers.get("x-powered-by"),
                "content_encoding": headers.get("content-encoding"),
                "transfer_encoding": headers.get("transfer-encoding"),
            }

            return {
                "http2_support": http2_support,
                "ssl_enabled": url.startswith("https://"),
                "compression_enabled": bool(headers.get("content-encoding")),
                "caching_configured": bool(
                    headers.get("cache-control") or headers.get("expires")
                ),
                "security_headers": security_headers,
                "performance_headers": performance_headers,
                "server_info": server_info,
                "redirect_count": len(response.history),
            }

        except Exception as e:
            return {"analysis_error": str(e)}

    def _identify_optimization_opportunities(
        self, url: str, speed_data: Dict
    ) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities."""
        opportunities = []

        performance_data = speed_data["performance_metrics"]
        page_analysis = speed_data["page_analysis"]
        resource_analysis = speed_data["resource_analysis"]

        # Image optimization opportunity
        image_analysis = page_analysis.get("image_analysis", {})
        if image_analysis.get("total_images", 0) > 0:
            potential_savings = (
                image_analysis["total_images"] * 50
            )  # Estimated KB savings
            opportunities.append(
                {
                    "type": "Image Optimization",
                    "impact": "High" if potential_savings > 500 else "Medium",
                    "description": f"Optimize {image_analysis['total_images']} images for better compression",
                    "potential_savings_kb": potential_savings,
                    "effort": "Medium",
                }
            )

        # JavaScript optimization
        if resource_analysis["blocking_resources"] > 2:
            opportunities.append(
                {
                    "type": "JavaScript Optimization",
                    "impact": "High",
                    "description": f"Optimize {resource_analysis['blocking_resources']} render-blocking scripts",
                    "potential_savings_ms": resource_analysis["blocking_resources"]
                    * 100,
                    "effort": "Low",
                }
            )

        # Caching opportunity
        if not performance_data.get("cache_control"):
            opportunities.append(
                {
                    "type": "Browser Caching",
                    "impact": "High",
                    "description": "Enable browser caching to reduce repeat load times",
                    "potential_savings_percent": 30,
                    "effort": "Low",
                }
            )

        # Compression opportunity
        if not performance_data.get("content_encoding"):
            opportunities.append(
                {
                    "type": "Compression",
                    "impact": "Medium",
                    "description": "Enable Gzip/Brotli compression to reduce file sizes",
                    "potential_savings_percent": 20,
                    "effort": "Low",
                }
            )

        return opportunities[:6]  # Top 6 opportunities

    def _generate_competitive_insights(self, speed_score: int) -> Dict[str, Any]:
        """Generate competitive performance insights."""
        # Simulated benchmarks based on industry data
        industry_benchmarks = {
            "ecommerce": {"avg_score": 65, "top_10_percent": 85},
            "news": {"avg_score": 60, "top_10_percent": 80},
            "blog": {"avg_score": 70, "top_10_percent": 90},
            "business": {"avg_score": 75, "top_10_percent": 90},
            "portfolio": {"avg_score": 80, "top_10_percent": 95},
        }

        # Estimate category based on score range
        estimated_category = "business"  # Default

        benchmark = industry_benchmarks[estimated_category]
        percentile = self._calculate_percentile(speed_score, benchmark)

        return {
            "estimated_category": estimated_category,
            "industry_average": benchmark["avg_score"],
            "top_10_percent_threshold": benchmark["top_10_percent"],
            "your_percentile": percentile,
            "performance_vs_average": speed_score - benchmark["avg_score"],
            "recommendation": self._get_competitive_recommendation(percentile),
        }

    def _calculate_percentile(self, score: int, benchmark: Dict) -> int:
        """Calculate approximate percentile based on score."""
        if score >= benchmark["top_10_percent"]:
            return 90 + min(10, (score - benchmark["top_10_percent"]) / 2)
        elif score >= benchmark["avg_score"]:
            return (
                50
                + (
                    (score - benchmark["avg_score"])
                    / (benchmark["top_10_percent"] - benchmark["avg_score"])
                )
                * 40
            )
        else:
            return max(1, (score / benchmark["avg_score"]) * 50)

    def _get_competitive_recommendation(self, percentile: int) -> str:
        """Get competitive recommendation based on percentile."""
        if percentile >= 90:
            return "Excellent! Your site outperforms 90% of similar websites."
        elif percentile >= 75:
            return "Good performance. Consider minor optimizations to reach top 10%."
        elif percentile >= 50:
            return "Average performance. Focus on key optimizations for competitive advantage."
        else:
            return (
                "Below average. Significant improvements needed to compete effectively."
            )
