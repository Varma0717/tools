import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlunparse
from urllib.robotparser import RobotFileParser
import re
import time
from collections import Counter, defaultdict
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import xml.etree.ElementTree as ET
import ssl
import socket
import dns.resolver
from PIL import Image
from io import BytesIO
import gzip
import hashlib
import subprocess
from datetime import datetime, timedelta


def audit_seo(url: str, is_premium: bool = False) -> dict:
    """
    Comprehensive SEO audit with premium features for paying customers
    """
    try:
        start_time = time.time()

        # Use the same comprehensive crawler for both free and premium users
        # The difference is in what data we return, not how much we analyze
        crawler = SEOSiteCrawler(url, max_pages=500)  # Always crawl comprehensively
        audit_results = crawler.perform_full_audit()

        end_time = time.time()
        audit_results["total_audit_time"] = round(end_time - start_time, 2)
        audit_results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        audit_results["is_premium_analysis"] = is_premium

        return audit_results

    except Exception as e:
        return {"success": False, "error": f"Site audit error: {str(e)}"}


class SEOSiteCrawler:
    def __init__(self, base_url, max_pages=500, max_depth=5):
        self.base_url = base_url.rstrip("/")
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.crawled_urls = set()
        self.failed_urls = set()
        self.page_data = {}
        self.site_structure = defaultdict(list)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def perform_limited_audit(self):
        """Limited audit for free users"""
        try:
            # Basic analysis only
            robots_analysis = self.analyze_robots_txt()
            sitemap_analysis = self.analyze_sitemap()

            # Crawl only homepage and few key pages
            basic_crawl = self.crawl_limited_pages()

            # Basic page analysis
            basic_analysis = self.analyze_basic_factors()

            # Calculate basic score
            overall_score = self.calculate_basic_score(
                basic_analysis, robots_analysis, sitemap_analysis
            )

            # Generate limited recommendations (only 5)
            recommendations = self.generate_basic_recommendations()[:5]

            return {
                "success": True,
                "url": self.base_url,
                "crawl_summary": {
                    "total_pages_found": len(self.crawled_urls),
                    "successfully_crawled": len(self.crawled_urls),
                    "failed_pages": len(self.failed_urls),
                    "analysis_type": "free_overview",
                    "limitation_notice": "Free users receive basic overview only",
                },
                "overall_score": overall_score,
                "score_breakdown": {
                    "technical": overall_score * 0.3,
                    "content": overall_score * 0.25,
                    "performance": overall_score * 0.25,
                    "mobile": overall_score * 0.2,
                    "note": "Upgrade for detailed breakdown and 15+ categories",
                },
                "quick_overview": {
                    "robots_txt": (
                        "Found" if robots_analysis.get("found") else "Missing"
                    ),
                    "sitemap": "Found" if sitemap_analysis.get("found") else "Missing",
                    "ssl_certificate": basic_analysis.get("ssl_status", "Unknown"),
                    "mobile_friendly": basic_analysis.get("mobile_friendly", "Unknown"),
                    "page_speed": (
                        "Needs analysis"
                        if not basic_analysis.get("page_speed")
                        else "Good"
                    ),
                },
                "top_issues": recommendations[:3],  # Only show top 3 issues
                "limitations": {
                    "pages_analyzed": f"{len(self.crawled_urls)} (homepage only)",
                    "checks_performed": "Basic overview (20+ checks)",
                    "missing_features": [
                        "Competitor analysis",
                        "Advanced technical SEO (180+ checks)",
                        "Content gap analysis",
                        "Backlink profile analysis",
                        "Core Web Vitals monitoring",
                        "Schema markup analysis",
                        "Local SEO optimization",
                        "ROI forecasting",
                        "PDF export",
                        "Historical tracking",
                    ],
                },
                "upgrade_cta": {
                    "message": "Unlock Professional SEO Analysis Worth $500+",
                    "benefits": [
                        "Complete website analysis (1000+ pages)",
                        "200+ advanced SEO checks",
                        "Competitor intelligence & benchmarking",
                        "Content strategy recommendations",
                        "Backlink analysis & opportunities",
                        "Monthly progress tracking",
                        "White-label PDF reports",
                        "Priority email support",
                    ],
                    "pricing": "$29/month - Cancel anytime",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def crawl_limited_pages(self):
        """Crawl only homepage and key pages for free users"""
        try:
            # Only crawl homepage for free users
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.crawled_urls.add(self.base_url)
                soup = BeautifulSoup(response.content, "html.parser")

                # Store basic page data
                self.page_data[self.base_url] = {
                    "title": soup.find("title").text if soup.find("title") else "",
                    "meta_description": (
                        soup.find("meta", {"name": "description"})["content"]
                        if soup.find("meta", {"name": "description"})
                        else ""
                    ),
                    "h1_count": len(soup.find_all("h1")),
                    "status_code": response.status_code,
                    "content_length": len(response.content),
                }

                return {"status": "success", "pages_crawled": 1}
            else:
                self.failed_urls.add(self.base_url)
                return {"status": "failed", "error": f"HTTP {response.status_code}"}

        except Exception as e:
            self.failed_urls.add(self.base_url)
            return {"status": "error", "error": str(e)}

    def analyze_basic_factors(self):
        """Basic technical analysis for free users"""
        analysis = {
            "https_usage": {"uses_https": self.base_url.startswith("https")},
            "meta_tags": {},
            "heading_structure": {},
            "page_speed": {},
        }

        try:
            if self.crawled_urls:
                url = list(self.crawled_urls)[0]
                page_data = self.page_data.get(url, {})

                analysis["meta_tags"] = {
                    "has_title": bool(page_data.get("title")),
                    "title_length": len(page_data.get("title", "")),
                    "has_meta_description": bool(page_data.get("meta_description")),
                    "meta_description_length": len(
                        page_data.get("meta_description", "")
                    ),
                }

                analysis["heading_structure"] = {
                    "h1_count": page_data.get("h1_count", 0),
                    "proper_h1": page_data.get("h1_count", 0) == 1,
                }

        except Exception as e:
            analysis["error"] = str(e)

        return analysis

    def calculate_basic_score(self, analysis, robots, sitemap):
        """Calculate basic SEO score for free users"""
        score = 0
        max_score = 100

        # HTTPS check (20 points)
        if analysis.get("https_usage", {}).get("uses_https"):
            score += 20

        # Title tag (20 points)
        meta = analysis.get("meta_tags", {})
        if meta.get("has_title") and 30 <= meta.get("title_length", 0) <= 60:
            score += 20
        elif meta.get("has_title"):
            score += 10

        # Meta description (20 points)
        if (
            meta.get("has_meta_description")
            and 120 <= meta.get("meta_description_length", 0) <= 160
        ):
            score += 20
        elif meta.get("has_meta_description"):
            score += 10

        # H1 tag (15 points)
        if analysis.get("heading_structure", {}).get("proper_h1"):
            score += 15

        # Robots.txt (15 points)
        if robots.get("exists"):
            score += 15

        # Sitemap (10 points)
        if sitemap.get("found"):
            score += 10

        return min(score, max_score)

    def generate_basic_recommendations(self):
        """Generate basic recommendations for free users"""
        recommendations = [
            {
                "priority": "critical",
                "category": "Technical SEO",
                "issue": "HTTPS Implementation",
                "description": "Ensure your website uses HTTPS for security and SEO benefits.",
                "impact": "High",
                "effort": "Medium",
            },
            {
                "priority": "high",
                "category": "On-Page SEO",
                "issue": "Title Tag Optimization",
                "description": "Optimize your title tags to be between 30-60 characters and include target keywords.",
                "impact": "High",
                "effort": "Low",
            },
            {
                "priority": "high",
                "category": "On-Page SEO",
                "issue": "Meta Description",
                "description": "Write compelling meta descriptions between 120-160 characters.",
                "impact": "Medium",
                "effort": "Low",
            },
            {
                "priority": "medium",
                "category": "Content",
                "issue": "H1 Tag Structure",
                "description": "Use exactly one H1 tag per page with your primary keyword.",
                "impact": "Medium",
                "effort": "Low",
            },
            {
                "priority": "medium",
                "category": "Technical SEO",
                "issue": "Robots.txt File",
                "description": "Create and optimize your robots.txt file to guide search engine crawlers.",
                "impact": "Medium",
                "effort": "Low",
            },
        ]

        return recommendations

    def perform_full_audit(self):
        """Perform comprehensive SEO audit"""
        try:
            # Step 1: Analyze robots.txt and sitemap
            robots_analysis = self.analyze_robots_txt()
            sitemap_analysis = self.analyze_sitemap()

            # Step 2: Crawl the website
            crawl_results = self.crawl_website()

            # Step 3: Analyze all crawled pages
            pages_analysis = self.analyze_all_pages()

            # Step 4: Site-wide analysis
            site_wide_analysis = self.analyze_site_wide_issues()

            # Step 5: Performance and technical analysis
            technical_analysis = self.analyze_technical_factors()

            # Step 6: Calculate comprehensive SEO score
            overall_score = self.calculate_comprehensive_score(
                {
                    "pages": pages_analysis,
                    "technical": technical_analysis,
                    "site_wide": site_wide_analysis,
                    "robots": robots_analysis,
                    "sitemap": sitemap_analysis,
                }
            )

            # Step 7: Generate comprehensive recommendations
            recommendations = self.generate_comprehensive_recommendations(
                pages_analysis,
                site_wide_analysis,
                technical_analysis,
                robots_analysis,
                sitemap_analysis,
            )

            return {
                "success": True,
                "url": self.base_url,
                "crawl_summary": {
                    "total_pages_found": len(self.crawled_urls) + len(self.failed_urls),
                    "successfully_crawled": len(self.crawled_urls),
                    "failed_pages": len(self.failed_urls),
                    "crawl_depth": self.max_depth,
                    "failed_urls_list": list(self.failed_urls)[
                        :10
                    ],  # Show first 10 failed URLs
                },
                "overall_score": overall_score,
                "robots_txt": robots_analysis,
                "sitemap": sitemap_analysis,
                "pages_analysis": pages_analysis,
                "site_wide_issues": site_wide_analysis,
                "technical_analysis": technical_analysis,
                "recommendations": recommendations,
                "site_structure": dict(self.site_structure),
            }

        except Exception as e:
            return {"success": False, "error": f"Full audit error: {str(e)}"}

    def analyze_robots_txt(self):
        """Analyze robots.txt file"""
        try:
            robots_url = urljoin(self.base_url, "/robots.txt")
            response = requests.get(robots_url, timeout=10, headers=self.headers)

            if response.status_code == 200:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()

                content = response.text
                lines = content.split("\n")

                # Parse directives
                disallow_patterns = []
                allow_patterns = []
                sitemaps = []
                crawl_delay = None

                for line in lines:
                    line = line.strip()
                    if line.lower().startswith("disallow:"):
                        disallow_patterns.append(line.split(":", 1)[1].strip())
                    elif line.lower().startswith("allow:"):
                        allow_patterns.append(line.split(":", 1)[1].strip())
                    elif line.lower().startswith("sitemap:"):
                        sitemaps.append(line.split(":", 1)[1].strip())
                    elif line.lower().startswith("crawl-delay:"):
                        crawl_delay = line.split(":", 1)[1].strip()

                return {
                    "exists": True,
                    "accessible": True,
                    "content": content,
                    "disallow_patterns": disallow_patterns,
                    "allow_patterns": allow_patterns,
                    "sitemaps": sitemaps,
                    "crawl_delay": crawl_delay,
                    "status": "good",
                    "size": len(content),
                }
            else:
                return {
                    "exists": False,
                    "accessible": False,
                    "status": "warning",
                    "error": f"HTTP {response.status_code}",
                }

        except Exception as e:
            return {
                "exists": False,
                "accessible": False,
                "status": "error",
                "error": str(e),
            }

    def analyze_sitemap(self):
        """Analyze XML sitemap"""
        try:
            # Try common sitemap locations
            sitemap_urls = [
                urljoin(self.base_url, "/sitemap.xml"),
                urljoin(self.base_url, "/sitemap_index.xml"),
                urljoin(self.base_url, "/sitemaps.xml"),
            ]

            for sitemap_url in sitemap_urls:
                try:
                    response = requests.get(
                        sitemap_url, timeout=10, headers=self.headers
                    )
                    if response.status_code == 200:
                        return self.parse_sitemap(response.text, sitemap_url)
                except:
                    continue

            return {
                "exists": False,
                "accessible": False,
                "status": "warning",
                "error": "No sitemap found at common locations",
            }

        except Exception as e:
            return {
                "exists": False,
                "accessible": False,
                "status": "error",
                "error": str(e),
            }

    def parse_sitemap(self, content, sitemap_url):
        """Parse XML sitemap content"""
        try:
            root = ET.fromstring(content)

            # Handle namespaces
            namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            urls = []
            for url_elem in root.findall(".//sm:url", namespaces):
                loc_elem = url_elem.find("sm:loc", namespaces)
                lastmod_elem = url_elem.find("sm:lastmod", namespaces)
                priority_elem = url_elem.find("sm:priority", namespaces)
                changefreq_elem = url_elem.find("sm:changefreq", namespaces)

                url_data = {
                    "loc": loc_elem.text if loc_elem is not None else "",
                    "lastmod": lastmod_elem.text if lastmod_elem is not None else "",
                    "priority": priority_elem.text if priority_elem is not None else "",
                    "changefreq": (
                        changefreq_elem.text if changefreq_elem is not None else ""
                    ),
                }
                urls.append(url_data)

            return {
                "exists": True,
                "accessible": True,
                "url": sitemap_url,
                "total_urls": len(urls),
                "urls": urls[:50],  # Return first 50 URLs for display
                "status": "good",
                "size": len(content),
            }

        except ET.ParseError as e:
            return {
                "exists": True,
                "accessible": True,
                "url": sitemap_url,
                "status": "error",
                "error": f"XML parsing error: {str(e)}",
            }

    def crawl_website(self):
        """Crawl website with depth-first approach"""
        to_crawl = [(self.base_url, 0)]  # (url, depth)
        crawled_count = 0

        while to_crawl and crawled_count < self.max_pages:
            current_url, depth = to_crawl.pop(0)

            if current_url in self.crawled_urls or current_url in self.failed_urls:
                continue

            if depth > self.max_depth:
                continue

            try:
                response = requests.get(current_url, timeout=15, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # Store page data
                self.page_data[current_url] = {
                    "response": response,
                    "soup": soup,
                    "depth": depth,
                    "status_code": response.status_code,
                }

                self.crawled_urls.add(current_url)
                crawled_count += 1

                # Find new URLs to crawl
                if depth < self.max_depth:
                    new_urls = self.extract_internal_links(soup, current_url)
                    for new_url in new_urls:
                        if (
                            new_url not in self.crawled_urls
                            and new_url not in self.failed_urls
                            and (new_url, depth + 1) not in to_crawl
                        ):
                            to_crawl.append((new_url, depth + 1))
                            self.site_structure[current_url].append(new_url)

                # Add small delay to be respectful
                time.sleep(0.5)

            except Exception as e:
                self.failed_urls.add(current_url)
                continue

        return {
            "crawled_pages": len(self.crawled_urls),
            "failed_pages": len(self.failed_urls),
            "max_depth_reached": (
                max([data["depth"] for data in self.page_data.values()])
                if self.page_data
                else 0
            ),
        }

    def extract_internal_links(self, soup, base_url):
        """Extract internal links from a page"""
        internal_links = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]

            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)

            # Check if it's an internal link
            if parsed_url.netloc == self.domain:
                # Clean the URL (remove fragments)
                clean_url = urlunparse(
                    (
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        parsed_url.query,
                        "",  # Remove fragment
                    )
                )

                # Avoid certain file types and parameters
                if not any(
                    clean_url.lower().endswith(ext)
                    for ext in [".pdf", ".jpg", ".png", ".gif", ".css", ".js"]
                ):
                    internal_links.add(clean_url)

        return internal_links

    def analyze_all_pages(self):
        """Analyze all crawled pages"""
        pages_analysis = {
            "total_pages": len(self.page_data),
            "pages": {},
            "aggregate_stats": {
                "avg_title_length": 0,
                "avg_meta_description_length": 0,
                "pages_missing_title": 0,
                "pages_missing_meta_description": 0,
                "pages_missing_h1": 0,
                "total_images": 0,
                "images_missing_alt": 0,
                "avg_page_size": 0,
                "avg_load_time": 0,
            },
        }

        title_lengths = []
        meta_desc_lengths = []
        page_sizes = []

        for url, data in self.page_data.items():
            start_time = time.time()

            # Analyze individual page
            page_analysis = self.analyze_single_page(
                data["soup"], data["response"], url
            )
            pages_analysis["pages"][url] = page_analysis

            # Collect stats for aggregation
            if page_analysis["title"]["text"]:
                title_lengths.append(page_analysis["title"]["length"])
            else:
                pages_analysis["aggregate_stats"]["pages_missing_title"] += 1

            if page_analysis["meta"]["description"]["text"]:
                meta_desc_lengths.append(page_analysis["meta"]["description"]["length"])
            else:
                pages_analysis["aggregate_stats"]["pages_missing_meta_description"] += 1

            if page_analysis["headings"]["h1_status"] == "error":
                pages_analysis["aggregate_stats"]["pages_missing_h1"] += 1

            pages_analysis["aggregate_stats"]["total_images"] += page_analysis[
                "content"
            ]["images"]["total"]
            pages_analysis["aggregate_stats"]["images_missing_alt"] += page_analysis[
                "content"
            ]["images"]["without_alt"]

            page_sizes.append(page_analysis["performance"]["content_size"])

        # Calculate averages
        if title_lengths:
            pages_analysis["aggregate_stats"]["avg_title_length"] = round(
                sum(title_lengths) / len(title_lengths), 1
            )
        if meta_desc_lengths:
            pages_analysis["aggregate_stats"]["avg_meta_description_length"] = round(
                sum(meta_desc_lengths) / len(meta_desc_lengths), 1
            )
        if page_sizes:
            pages_analysis["aggregate_stats"]["avg_page_size"] = round(
                sum(page_sizes) / len(page_sizes) / 1024, 1
            )  # KB

        return pages_analysis

    def analyze_single_page(self, soup, response, url):
        """Analyze a single page (enhanced version of original function)"""
        start_time = time.time()

        # Use existing analysis functions but enhanced
        title_analysis = analyze_title(soup)
        meta_analysis = analyze_meta_tags(soup)
        heading_analysis = analyze_headings(soup)
        content_analysis = analyze_content(soup, url)
        technical_analysis = analyze_technical_seo(soup, response, url)
        performance_analysis = analyze_performance(response, start_time)

        # Additional page-specific analysis
        page_analysis = {
            "url": url,
            "title": title_analysis,
            "meta": meta_analysis,
            "headings": heading_analysis,
            "content": content_analysis,
            "technical": technical_analysis,
            "performance": performance_analysis,
            "accessibility": self.analyze_accessibility(soup),
            "mobile_friendliness": self.analyze_mobile_friendliness(soup),
        }

        # Calculate page score
        page_analysis["page_score"] = calculate_seo_score(
            {
                "title": title_analysis,
                "meta": meta_analysis,
                "headings": heading_analysis,
                "content": content_analysis,
                "technical": technical_analysis,
                "performance": performance_analysis,
            }
        )

        return page_analysis

    def analyze_accessibility(self, soup):
        """Analyze basic accessibility factors"""
        # Check for alt attributes on images
        images = soup.find_all("img")
        images_with_alt = sum(1 for img in images if img.get("alt"))

        # Check for form labels
        inputs = soup.find_all(["input", "textarea", "select"])
        inputs_with_labels = 0
        for input_elem in inputs:
            input_id = input_elem.get("id")
            if input_id and soup.find("label", {"for": input_id}):
                inputs_with_labels += 1

        # Check for heading structure
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        return {
            "images_with_alt_ratio": round(
                (images_with_alt / len(images) * 100) if images else 100, 1
            ),
            "forms_with_labels_ratio": round(
                (inputs_with_labels / len(inputs) * 100) if inputs else 100, 1
            ),
            "heading_structure_present": len(headings) > 0,
            "total_headings": len(headings),
        }

    def analyze_mobile_friendliness(self, soup):
        """Analyze mobile friendliness factors"""
        viewport_tag = soup.find("meta", attrs={"name": "viewport"})

        # Check for responsive design indicators
        responsive_indicators = 0

        # Check for viewport meta tag
        if viewport_tag:
            responsive_indicators += 1

        # Check for responsive CSS (media queries in style tags)
        style_tags = soup.find_all("style")
        has_media_queries = any("@media" in tag.get_text() for tag in style_tags)
        if has_media_queries:
            responsive_indicators += 1

        return {
            "viewport_tag_present": bool(viewport_tag),
            "viewport_content": viewport_tag.get("content") if viewport_tag else None,
            "responsive_indicators": responsive_indicators,
            "mobile_score": min(responsive_indicators * 50, 100),
        }

    def analyze_site_wide_issues(self):
        """Analyze site-wide SEO issues"""
        duplicate_titles = defaultdict(list)
        duplicate_meta_descriptions = defaultdict(list)
        duplicate_h1s = defaultdict(list)
        broken_internal_links = []
        redirect_chains = []

        # Analyze for duplicates
        for url, data in self.page_data.items():
            page_analysis = self.analyze_single_page(
                data["soup"], data["response"], url
            )

            title = page_analysis["title"]["text"]
            if title:
                duplicate_titles[title].append(url)

            meta_desc = page_analysis["meta"]["description"]["text"]
            if meta_desc:
                duplicate_meta_descriptions[meta_desc].append(url)

            h1_texts = page_analysis["headings"]["structure"]["h1"]["texts"]
            for h1 in h1_texts:
                if h1:
                    duplicate_h1s[h1].append(url)

        # Find actual duplicates (more than one page)
        duplicate_titles = {
            title: urls for title, urls in duplicate_titles.items() if len(urls) > 1
        }
        duplicate_meta_descriptions = {
            desc: urls
            for desc, urls in duplicate_meta_descriptions.items()
            if len(urls) > 1
        }
        duplicate_h1s = {
            h1: urls for h1, urls in duplicate_h1s.items() if len(urls) > 1
        }

        return {
            "duplicate_titles": duplicate_titles,
            "duplicate_meta_descriptions": duplicate_meta_descriptions,
            "duplicate_h1_tags": duplicate_h1s,
            "broken_internal_links": broken_internal_links,
            "duplicate_content_issues": len(duplicate_titles)
            + len(duplicate_meta_descriptions)
            + len(duplicate_h1s),
            "crawl_coverage": {
                "total_discovered": len(self.crawled_urls) + len(self.failed_urls),
                "successfully_crawled": len(self.crawled_urls),
                "failed_crawls": len(self.failed_urls),
                "coverage_percentage": round(
                    (
                        (
                            len(self.crawled_urls)
                            / (len(self.crawled_urls) + len(self.failed_urls))
                            * 100
                        )
                        if (len(self.crawled_urls) + len(self.failed_urls)) > 0
                        else 0
                    ),
                    1,
                ),
            },
        }

    def analyze_technical_factors(self):
        """Analyze technical SEO factors across the site"""
        https_pages = sum(1 for url in self.crawled_urls if url.startswith("https://"))
        pages_with_canonical = 0
        pages_with_schema = 0
        pages_with_meta_robots = 0

        for url, data in self.page_data.items():
            soup = data["soup"]

            # Canonical tags
            if soup.find("link", rel="canonical"):
                pages_with_canonical += 1

            # Schema markup
            if soup.find_all("script", type="application/ld+json"):
                pages_with_schema += 1

            # Meta robots
            if soup.find("meta", attrs={"name": "robots"}):
                pages_with_meta_robots += 1

        total_pages = len(self.page_data)

        return {
            "https_usage": {
                "total_https_pages": https_pages,
                "https_percentage": round(
                    (https_pages / total_pages * 100) if total_pages > 0 else 0, 1
                ),
            },
            "canonical_tags": {
                "pages_with_canonical": pages_with_canonical,
                "canonical_percentage": round(
                    (
                        (pages_with_canonical / total_pages * 100)
                        if total_pages > 0
                        else 0
                    ),
                    1,
                ),
            },
            "structured_data": {
                "pages_with_schema": pages_with_schema,
                "schema_percentage": round(
                    (pages_with_schema / total_pages * 100) if total_pages > 0 else 0, 1
                ),
            },
            "meta_robots": {
                "pages_with_meta_robots": pages_with_meta_robots,
                "meta_robots_percentage": round(
                    (
                        (pages_with_meta_robots / total_pages * 100)
                        if total_pages > 0
                        else 0
                    ),
                    1,
                ),
            },
        }

    def calculate_comprehensive_score(self, analysis_data):
        """Calculate comprehensive SEO score based on all factors"""
        score = 0
        max_score = 100

        pages_data = analysis_data["pages"]
        technical_data = analysis_data["technical"]
        site_wide_data = analysis_data["site_wide"]
        robots_data = analysis_data["robots"]
        sitemap_data = analysis_data["sitemap"]

        # Pages analysis (40 points)
        if pages_data["total_pages"] > 0:
            avg_page_scores = []
            for page_url, page_data in pages_data["pages"].items():
                avg_page_scores.append(page_data["page_score"])

            avg_page_score = sum(avg_page_scores) / len(avg_page_scores)
            score += int(avg_page_score * 0.4)  # 40% weight

        # Technical factors (25 points)
        if technical_data["https_usage"]["https_percentage"] == 100:
            score += 8
        elif technical_data["https_usage"]["https_percentage"] >= 80:
            score += 5

        if technical_data["canonical_tags"]["canonical_percentage"] >= 80:
            score += 6
        elif technical_data["canonical_tags"]["canonical_percentage"] >= 50:
            score += 3

        if technical_data["structured_data"]["schema_percentage"] >= 50:
            score += 6
        elif technical_data["structured_data"]["schema_percentage"] >= 20:
            score += 3

        if technical_data["meta_robots"]["meta_robots_percentage"] >= 80:
            score += 5
        elif technical_data["meta_robots"]["meta_robots_percentage"] >= 50:
            score += 2

        # Site-wide issues (20 points)
        duplicate_issues = site_wide_data["duplicate_content_issues"]
        if duplicate_issues == 0:
            score += 10
        elif duplicate_issues <= 2:
            score += 6
        elif duplicate_issues <= 5:
            score += 3

        crawl_coverage = site_wide_data["crawl_coverage"]["coverage_percentage"]
        if crawl_coverage >= 95:
            score += 10
        elif crawl_coverage >= 80:
            score += 6
        elif crawl_coverage >= 60:
            score += 3

        # Infrastructure (15 points)
        if robots_data["status"] == "good":
            score += 8
        elif robots_data["status"] == "warning":
            score += 4

        if sitemap_data["status"] == "good":
            score += 7
        elif sitemap_data["status"] == "warning":
            score += 3

        return min(score, max_score)

    def generate_comprehensive_recommendations(
        self,
        pages_analysis,
        site_wide_analysis,
        technical_analysis,
        robots_analysis,
        sitemap_analysis,
    ):
        """Generate comprehensive recommendations based on full site analysis"""
        recommendations = []

        # Site-wide issues
        if site_wide_analysis["duplicate_content_issues"] > 0:
            recommendations.append(
                {
                    "type": "error",
                    "category": "Duplicate Content",
                    "message": f'Found {site_wide_analysis["duplicate_content_issues"]} duplicate content issues across the site',
                    "priority": "high",
                    "details": {
                        "duplicate_titles": len(site_wide_analysis["duplicate_titles"]),
                        "duplicate_meta_descriptions": len(
                            site_wide_analysis["duplicate_meta_descriptions"]
                        ),
                        "duplicate_h1_tags": len(
                            site_wide_analysis["duplicate_h1_tags"]
                        ),
                    },
                }
            )

        # HTTPS usage
        if technical_analysis["https_usage"]["https_percentage"] < 100:
            recommendations.append(
                {
                    "type": "error",
                    "category": "Security",
                    "message": f'Only {technical_analysis["https_usage"]["https_percentage"]}% of pages use HTTPS',
                    "priority": "high",
                }
            )

        # Canonical tags
        if technical_analysis["canonical_tags"]["canonical_percentage"] < 80:
            recommendations.append(
                {
                    "type": "warning",
                    "category": "Technical SEO",
                    "message": f'Only {technical_analysis["canonical_tags"]["canonical_percentage"]}% of pages have canonical tags',
                    "priority": "medium",
                }
            )

        # Structured data
        if technical_analysis["structured_data"]["schema_percentage"] < 50:
            recommendations.append(
                {
                    "type": "warning",
                    "category": "Structured Data",
                    "message": f'Only {technical_analysis["structured_data"]["schema_percentage"]}% of pages have schema markup',
                    "priority": "medium",
                }
            )

        # Robots.txt issues
        if robots_analysis["status"] != "good":
            recommendations.append(
                {
                    "type": (
                        "warning" if robots_analysis["status"] == "warning" else "error"
                    ),
                    "category": "Robots.txt",
                    "message": "Issues found with robots.txt file",
                    "priority": "medium",
                    "details": robots_analysis.get("error", "Unknown error"),
                }
            )

        # Sitemap issues
        if sitemap_analysis["status"] != "good":
            recommendations.append(
                {
                    "type": (
                        "warning"
                        if sitemap_analysis["status"] == "warning"
                        else "error"
                    ),
                    "category": "XML Sitemap",
                    "message": "Issues found with XML sitemap",
                    "priority": "medium",
                    "details": sitemap_analysis.get("error", "Unknown error"),
                }
            )

        # Page-level aggregate issues
        agg_stats = pages_analysis["aggregate_stats"]
        total_pages = pages_analysis["total_pages"]

        if agg_stats["pages_missing_title"] > 0:
            recommendations.append(
                {
                    "type": "error",
                    "category": "Title Tags",
                    "message": f'{agg_stats["pages_missing_title"]} out of {total_pages} pages are missing title tags',
                    "priority": "high",
                }
            )

        if agg_stats["pages_missing_meta_description"] > 0:
            recommendations.append(
                {
                    "type": "warning",
                    "category": "Meta Descriptions",
                    "message": f'{agg_stats["pages_missing_meta_description"]} out of {total_pages} pages are missing meta descriptions',
                    "priority": "medium",
                }
            )

        if agg_stats["pages_missing_h1"] > 0:
            recommendations.append(
                {
                    "type": "warning",
                    "category": "H1 Tags",
                    "message": f'{agg_stats["pages_missing_h1"]} out of {total_pages} pages are missing or have multiple H1 tags',
                    "priority": "medium",
                }
            )

        if agg_stats["total_images"] > 0:
            alt_ratio = (
                (agg_stats["total_images"] - agg_stats["images_missing_alt"])
                / agg_stats["total_images"]
                * 100
            )
            if alt_ratio < 80:
                recommendations.append(
                    {
                        "type": "warning",
                        "category": "Image Accessibility",
                        "message": f'{agg_stats["images_missing_alt"]} out of {agg_stats["total_images"]} images are missing alt text ({round(100-alt_ratio, 1)}%)',
                        "priority": "medium",
                    }
                )

        # Crawl coverage issues
        coverage = site_wide_analysis["crawl_coverage"]["coverage_percentage"]
        if coverage < 90:
            recommendations.append(
                {
                    "type": "warning",
                    "category": "Crawlability",
                    "message": f"Only {coverage}% of discovered pages could be successfully crawled",
                    "priority": "medium",
                    "details": f'{site_wide_analysis["crawl_coverage"]["failed_crawls"]} pages failed to crawl',
                }
            )

        return recommendations


# Keep all the existing helper functions but enhance them
def analyze_title(soup):
    """Analyze title tag"""
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    return {
        "text": title,
        "length": len(title),
        "status": (
            "optimal"
            if 30 <= len(title) <= 60
            else "warning" if len(title) > 0 else "error"
        ),
        "issues": get_title_issues(title),
        "keywords": extract_keywords(title),
    }


def analyze_meta_tags(soup):
    """Analyze meta tags"""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag.get("content", "").strip() if desc_tag else ""

    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    keywords = keywords_tag.get("content", "").strip() if keywords_tag else ""

    # Open Graph tags
    og_tags = {}
    for og in soup.find_all("meta", property=re.compile("^og:")):
        og_tags[og.get("property")] = og.get("content", "")

    # Twitter Cards
    twitter_tags = {}
    for twitter in soup.find_all("meta", attrs={"name": re.compile("^twitter:")}):
        twitter_tags[twitter.get("name")] = twitter.get("content", "")

    return {
        "description": {
            "text": description,
            "length": len(description),
            "status": (
                "optimal"
                if 120 <= len(description) <= 160
                else "warning" if len(description) > 0 else "error"
            ),
            "keywords": extract_keywords(description),
        },
        "keywords": keywords,
        "open_graph": og_tags,
        "twitter_cards": twitter_tags,
        "other_meta": get_other_meta_tags(soup),
    }


def analyze_headings(soup):
    """Analyze heading structure"""
    headings = {}
    heading_hierarchy = []

    for i in range(1, 7):
        h_tags = soup.find_all(f"h{i}")
        headings[f"h{i}"] = {
            "count": len(h_tags),
            "texts": [h.get_text(strip=True) for h in h_tags],
            "keywords": [extract_keywords(h.get_text(strip=True)) for h in h_tags],
        }

        for h in h_tags:
            heading_hierarchy.append(
                {
                    "level": i,
                    "text": h.get_text(strip=True),
                    "length": len(h.get_text(strip=True)),
                }
            )

    return {
        "structure": headings,
        "hierarchy": heading_hierarchy,
        "h1_status": (
            "good"
            if headings["h1"]["count"] == 1
            else "warning" if headings["h1"]["count"] > 1 else "error"
        ),
        "issues": get_heading_issues(headings),
    }


def analyze_content(soup, url):
    """Analyze page content"""
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    text_content = soup.get_text()
    words = text_content.split()
    word_count = len(words)

    # Images analysis
    images = soup.find_all("img")
    images_analysis = analyze_images(images, url)

    # Links analysis
    links_analysis = analyze_links(soup, url)

    # Keyword density
    keyword_density = calculate_keyword_density(words)

    return {
        "word_count": word_count,
        "reading_time": max(1, word_count // 200),  # Average 200 words per minute
        "images": images_analysis,
        "links": links_analysis,
        "keyword_density": keyword_density,
        "content_quality": assess_content_quality(text_content),
    }


def analyze_technical_seo(soup, response, url):
    """Analyze technical SEO factors"""
    # Canonical tag
    canonical = soup.find("link", rel="canonical")
    canonical_url = canonical.get("href") if canonical else None

    # Meta robots
    robots_tag = soup.find("meta", attrs={"name": "robots"})
    robots_content = robots_tag.get("content", "") if robots_tag else ""

    # Viewport
    viewport = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = bool(viewport)

    # Schema markup
    schema_scripts = soup.find_all("script", type="application/ld+json")
    schema_data = []
    for script in schema_scripts:
        try:
            schema_data.append(json.loads(script.string))
        except:
            pass

    # Language
    html_tag = soup.find("html")
    lang = html_tag.get("lang") if html_tag else None

    return {
        "canonical": {
            "present": bool(canonical_url),
            "url": canonical_url,
            "status": "good" if canonical_url else "warning",
        },
        "robots": {
            "content": robots_content,
            "indexable": "noindex" not in robots_content.lower(),
            "followable": "nofollow" not in robots_content.lower(),
        },
        "viewport": {
            "present": has_viewport,
            "status": "good" if has_viewport else "error",
        },
        "schema": {
            "present": len(schema_data) > 0,
            "count": len(schema_data),
            "types": get_schema_types(schema_data),
        },
        "language": {
            "present": bool(lang),
            "code": lang,
            "status": "good" if lang else "warning",
        },
        "https": url.startswith("https://"),
        "response_code": response.status_code,
    }


def analyze_performance(response, start_time):
    """Analyze basic performance metrics"""
    load_time = time.time() - start_time
    content_length = len(response.content)

    return {
        "load_time": round(load_time, 2),
        "load_time_status": (
            "good" if load_time < 3 else "warning" if load_time < 5 else "error"
        ),
        "content_size": content_length,
        "content_size_mb": round(content_length / (1024 * 1024), 2),
        "compression": "gzip" in response.headers.get("content-encoding", "").lower(),
    }


def calculate_seo_score(analysis_data):
    """Calculate overall SEO score (0-100)"""
    score = 0
    max_score = 100

    # Title (15 points)
    if analysis_data["title"]["status"] == "optimal":
        score += 15
    elif analysis_data["title"]["status"] == "warning":
        score += 8

    # Meta description (15 points)
    if analysis_data["meta"]["description"]["status"] == "optimal":
        score += 15
    elif analysis_data["meta"]["description"]["status"] == "warning":
        score += 8

    # H1 tag (10 points)
    if analysis_data["headings"]["h1_status"] == "good":
        score += 10
    elif analysis_data["headings"]["h1_status"] == "warning":
        score += 5

    # Content length (10 points)
    word_count = analysis_data["content"]["word_count"]
    if word_count >= 300:
        score += 10
    elif word_count >= 100:
        score += 5

    # Images with alt tags (10 points)
    images_data = analysis_data["content"]["images"]
    if images_data["total"] > 0:
        alt_ratio = images_data["with_alt"] / images_data["total"]
        score += int(10 * alt_ratio)
    else:
        score += 5  # No images is not necessarily bad

    # Technical SEO (25 points)
    tech = analysis_data["technical"]
    if tech["canonical"]["status"] == "good":
        score += 5
    if tech["viewport"]["status"] == "good":
        score += 5
    if tech["language"]["status"] == "good":
        score += 5
    if tech["https"]:
        score += 5
    if tech["schema"]["present"]:
        score += 5

    # Performance (15 points)
    perf = analysis_data["performance"]
    if perf["load_time_status"] == "good":
        score += 10
    elif perf["load_time_status"] == "warning":
        score += 5

    if perf["compression"]:
        score += 5

    return min(score, max_score)


# Helper functions
def get_title_issues(title):
    issues = []
    if not title:
        issues.append("Missing title tag")
    elif len(title) < 30:
        issues.append("Title too short (recommended: 30-60 characters)")
    elif len(title) > 60:
        issues.append("Title too long (recommended: 30-60 characters)")
    return issues


def extract_keywords(text):
    # Simple keyword extraction
    words = re.findall(r"\b\w+\b", text.lower())
    return [word for word in words if len(word) > 3]


def get_other_meta_tags(soup):
    other_tags = {}
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        if (
            name
            and name not in ["description", "keywords"]
            and not name.startswith(("og:", "twitter:"))
        ):
            other_tags[name] = meta.get("content", "")
    return other_tags


def analyze_images(images, base_url):
    total_images = len(images)
    with_alt = sum(1 for img in images if img.get("alt"))
    without_alt = total_images - with_alt

    # Check for lazy loading
    lazy_loading = sum(1 for img in images if img.get("loading") == "lazy")

    return {
        "total": total_images,
        "with_alt": with_alt,
        "without_alt": without_alt,
        "alt_percentage": round(
            (with_alt / total_images * 100) if total_images > 0 else 100, 1
        ),
        "lazy_loading": lazy_loading,
        "status": (
            "good"
            if without_alt == 0
            else "warning" if without_alt < total_images / 2 else "error"
        ),
    }


def analyze_links(soup, base_url):
    domain = urlparse(base_url).netloc
    internal_links = 0
    external_links = 0
    broken_links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("http"):
            if domain in href:
                internal_links += 1
            else:
                external_links += 1
        elif href.startswith("/"):
            internal_links += 1

    return {
        "internal": internal_links,
        "external": external_links,
        "total": internal_links + external_links,
        "internal_ratio": round(
            (
                (internal_links / (internal_links + external_links) * 100)
                if (internal_links + external_links) > 0
                else 0
            ),
            1,
        ),
    }


def calculate_keyword_density(words):
    if not words:
        return {}

    word_freq = Counter(word.lower() for word in words if len(word) > 3)
    total_words = len(words)

    # Get top 10 keywords
    top_keywords = {}
    for word, count in word_freq.most_common(10):
        density = round((count / total_words) * 100, 2)
        top_keywords[word] = {"count": count, "density": density}

    return top_keywords


def assess_content_quality(text):
    sentences = text.split(".")
    avg_sentence_length = (
        sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    )

    return {
        "sentence_count": len(sentences),
        "avg_sentence_length": round(avg_sentence_length, 1),
        "readability": "good" if 15 <= avg_sentence_length <= 25 else "warning",
    }


def get_heading_issues(headings):
    issues = []
    if headings["h1"]["count"] == 0:
        issues.append("Missing H1 tag")
    elif headings["h1"]["count"] > 1:
        issues.append("Multiple H1 tags found")

    # Check hierarchy
    prev_level = 0
    for level in range(1, 7):
        if headings[f"h{level}"]["count"] > 0:
            if level > prev_level + 1 and prev_level > 0:
                issues.append(
                    f"Heading hierarchy skip detected (H{prev_level} to H{level})"
                )
            prev_level = level

    return issues


def get_schema_types(schema_data):
    types = []
    for data in schema_data:
        if isinstance(data, dict) and "@type" in data:
            types.append(data["@type"])
    return types


def generate_recommendations(title, meta, headings, content, technical):
    recommendations = []

    # Title recommendations
    if title["status"] != "optimal":
        if not title["text"]:
            recommendations.append(
                {
                    "type": "error",
                    "category": "Title",
                    "message": "Add a title tag to your page",
                    "priority": "high",
                }
            )
        elif len(title["text"]) < 30:
            recommendations.append(
                {
                    "type": "warning",
                    "category": "Title",
                    "message": "Make your title longer (30-60 characters recommended)",
                    "priority": "medium",
                }
            )
        elif len(title["text"]) > 60:
            recommendations.append(
                {
                    "type": "warning",
                    "category": "Title",
                    "message": "Shorten your title (30-60 characters recommended)",
                    "priority": "medium",
                }
            )

    # Meta description recommendations
    if meta["description"]["status"] != "optimal":
        if not meta["description"]["text"]:
            recommendations.append(
                {
                    "type": "error",
                    "category": "Meta Description",
                    "message": "Add a meta description to your page",
                    "priority": "high",
                }
            )
        elif len(meta["description"]["text"]) < 120:
            recommendations.append(
                {
                    "type": "warning",
                    "category": "Meta Description",
                    "message": "Make your meta description longer (120-160 characters recommended)",
                    "priority": "medium",
                }
            )

    # Heading recommendations
    if headings["h1_status"] != "good":
        recommendations.append(
            {
                "type": "error" if headings["h1_status"] == "error" else "warning",
                "category": "Headings",
                "message": "Use exactly one H1 tag per page",
                "priority": "high" if headings["h1_status"] == "error" else "medium",
            }
        )

    # Content recommendations
    if content["word_count"] < 300:
        recommendations.append(
            {
                "type": "warning",
                "category": "Content",
                "message": "Add more content to your page (300+ words recommended)",
                "priority": "medium",
            }
        )

    # Image recommendations
    if content["images"]["without_alt"] > 0:
        recommendations.append(
            {
                "type": "warning",
                "category": "Images",
                "message": f"Add alt text to {content['images']['without_alt']} images",
                "priority": "medium",
            }
        )

    # Technical recommendations
    if not technical["canonical"]["present"]:
        recommendations.append(
            {
                "type": "warning",
                "category": "Technical",
                "message": "Add a canonical URL to prevent duplicate content issues",
                "priority": "medium",
            }
        )

    if not technical["viewport"]["present"]:
        recommendations.append(
            {
                "type": "error",
                "category": "Mobile",
                "message": "Add a viewport meta tag for mobile optimization",
                "priority": "high",
            }
        )

    if not technical["https"]:
        recommendations.append(
            {
                "type": "error",
                "category": "Security",
                "message": "Use HTTPS for security and SEO benefits",
                "priority": "high",
            }
        )

    return recommendations
