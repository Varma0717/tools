from flask import Blueprint, render_template

# Import each tool's blueprint 
from .meta_tag_analyzer import meta_tag_analyzer_bp
from .open_graph_preview import open_graph_preview_bp
from .serp_snippet_preview import serp_snippet_preview_bp
from .broken_link_checker import broken_link_checker_bp

from .redirect_checker import redirect_checker_bp

from .find_all_links import find_all_links_bp
from .favicon_checker import favicon_checker_bp
from .ssl_checker import ssl_checker_bp
from .http_header_checker import http_header_checker_bp
from .crawlability_tester import crawlability_tester_bp



from .utm_builder import utm_builder_bp
from .ip_location_finder import ip_location_finder_bp
from .page_speed_analyzer import page_speed_analyzer_bp

from .keyword_suggestion_generator import keyword_suggestion_generator_bp
from .keyword_density_analyzer import keyword_density_analyzer_bp


from .lsi_keyword_generator import lsi_keyword_generator_bp

from .anchor_text_checker import anchor_text_checker_bp
from .broken_backlink_finder import broken_backlink_finder_bp
from .referring_domain_analyzer import referring_domain_analyzer_bp

from .meta_tag_generator import meta_tag_generator_bp
from .robots_txt_tester import robots_txt_tester_bp
from .sitemap_xml_validator import sitemap_xml_validator_bp
from .hreflang_tag_checker import hreflang_tag_checker_bp
from .canonical_tag_checker import canonical_tag_checker_bp

from .image_alt_text_checker import image_alt_text_checker_bp
from .image_compressor import image_compressor_bp
from .image_to_webp_converter import image_to_webp_converter_bp
from .image_dimension_checker import image_dimension_checker_bp


from .expiry_date_checker import expiry_date_checker_bp
from .whois_lookup import whois_lookup_bp
from .dns_lookup import dns_lookup_bp
from .reverse_ip_lookup import reverse_ip_lookup_bp

from .password_generator import password_generator_bp
from .password_strength_checker import password_strength_checker_bp

from .pdf_to_text_extractor import pdf_to_text_extractor_bp
from .pdf_compressor import pdf_compressor_bp
from .pdf_metadata_viewer import pdf_metadata_viewer_bp

from .json_ld_validator import json_ld_validator_bp
from .schema_markup_tester import schema_markup_tester_bp
from .amp_validator import amp_validator_bp


from .blog_outline_generator import blog_outline_generator_bp

from .faq_schema_generator import faq_schema_generator_bp

from .meta_description_generator import meta_description_generator_bp


from .readability_checker import readability_checker_bp
from .referring_domain_analyzer import referring_domain_analyzer_bp
from .reverse_ip_lookup import reverse_ip_lookup_bp
from .text_summarizer import text_summarizer_bp
from .title_tag_generator import title_tag_generator_bp

from .referrer_ip_tracker import referrer_ip_tracker_bp
from .request_rate_monitor import request_rate_monitor_bp
from .referrer_log_analyzer import referrer_log_analyzer_bp
from .click_fraud_detector import click_fraud_detector_bp
from .referrer_spam_filter import referrer_spam_filter_bp
from .conversion_funnel_tracker import conversion_funnel_tracker_bp
from .uptime_monitor import uptime_monitor_bp
from .bot_detection import bot_detection_bp
from .page_view_counter import page_view_counter_bp
from .writing_style_analyzer import writing_style_analyzer_bp
from .headline_generator import headline_generator_bp
from .ai_content_generator_basic import ai_content_generator_basic_bp
from .auto_title_generator import auto_title_generator_bp
from .grammar_checker import grammar_checker_bp
from .content_rewriter_pro import content_rewriter_pro_bp
from .text_summarizer_pro import text_summarizer_pro_bp
from .seo_content_score_calculator import seo_score_calculator_bp
from .content_enhancer import content_enhancer_bp
from .paraphrasing_tool import paraphrasing_tool_bp

from .link_status_monitor import link_status_monitor_bp
from .backlink_url_monitor import backlink_url_monitor_bp
from .internal_link_analyzer import internal_link_analyzer_bp
from .link_profile_analyzer import link_profile_analyzer_bp
from .internal_link_structure_analyzer import internal_link_structure_analyzer_bp
from .javascript_obfuscator import js_obfuscator_bp
from .javascript_beautifier import js_beautifier_bp
from .javascript_minifier import js_minifier_bp
from .mobile_optimization_tester import mobile_tester_bp
from .seo_audit_tool import seo_audit_tool_bp
from .code_linter import code_linter_bp
from .javascript_error_logger import js_error_logger_bp
from .css_js_bundler import bundler_bp
from .sitemap_generator import sitemap_bp
from .html_minifier import html_minifier_bp
from .robots_txt_generator import robots_bp
from .speed_test import speed_test_bp

tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

all_tools = [
    # -------- Meta Tags Tools --------
    {
        "name": "Meta Tag Analyzer",
        "endpoint": "meta_tag_analyzer.meta_tag_analyzer",
        "description": "Analyzes and scores important SEO-related meta tags visually.",
        "category": "Meta Tags Tools"
    },
    {
        "name": "Meta Tag Generator",
        "endpoint": "meta_tag_generator.meta_tag_generator",
        "description": "Generate meta tags for any website automatically.",
        "category": "Meta Tags Tools"
    },
    {
        "name": "Open Graph & Twitter Preview",
        "endpoint": "open_graph_preview.open_graph_preview",
        "description": "Preview how your page looks when shared on Facebook, LinkedIn, and Twitter.",
        "category": "Meta Tags Tools"
    },
    {
        "name": "SERP Snippet Preview Tool",
        "endpoint": "serp_snippet_preview.serp_snippet_preview",
        "description": "Preview how your title, meta description and URL appear in Google search results.",
        "category": "Meta Tags Tools"
    },
    {
        "name": "Robots.txt Tester/Generator",
        "endpoint": "robots_txt_tester.robots_txt_tester",
        "description": "Test and generate robots.txt files for your website.",
        "category": "Meta Tags Tools"
    },
    {
        "name": "Sitemap.xml Validator/Generator",
        "endpoint": "sitemap_xml_validator.sitemap_xml_validator",
        "description": "Validate or create your XML sitemaps easily.",
        "category": "Meta Tags Tools"
    },
    {
        "name": "Hreflang Tag Checker",
        "endpoint": "hreflang_tag_checker.hreflang_tag_checker",
        "description": "Check hreflang implementation for multi-language SEO.",
        "category": "Meta Tags Tools"
    },
    {
        "name": "Canonical Tag Checker",
        "endpoint": "canonical_tag_checker.canonical_tag_checker",
        "description": "Verify canonical tags and prevent duplicate content.",
        "category": "Meta Tags Tools"
    },

    # -------- Website Management Tools --------
    {
        "name": "Broken Link Checker",
        "endpoint": "broken_link_checker.broken_link_checker",
        "description": "Scan any web page and find broken or dead links in real-time.",
        "category": "Website Management Tools"
    },
    {
        "name": "Redirect Checker",
        "endpoint": "redirect_checker.redirect_checker",
        "description": "Check 301, 302 and meta refresh redirects.",
        "category": "Website Management Tools"
    },
   
    {
        "name": "Find All Links",
        "endpoint": "find_all_links.find_all_links",
        "description": "List all internal and external links on any page.",
        "category": "Website Management Tools"
    },
    {
        "name": "Favicon Checker",
        "endpoint": "favicon_checker.favicon_checker",
        "description": "Check and preview favicon presence and status.",
        "category": "Website Management Tools"
    },
    {
        "name": "SSL Checker",
        "endpoint": "ssl_checker.ssl_checker",
        "description": "Verify SSL/TLS certificates for security and SEO.",
        "category": "Website Management Tools"
    },
    
    {
        "name": "Crawlability/Indexability Tester",
        "endpoint": "crawlability_tester.crawlability_tester",
        "description": "Test if a page can be crawled and indexed by Google.",
        "category": "Website Management Tools"
    },

    # -------- Website Tracking Tools --------
   

    
    {
        "name": "UTM Builder",
        "endpoint": "utm_builder.utm_builder",
        "description": "Build UTM-tagged URLs for campaigns.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "IP Location Finder",
        "endpoint": "ip_location_finder.ip_location_finder",
        "description": "Check IP location for SEO and analytics.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Page Speed/Performance Analyzer",
        "endpoint": "page_speed_analyzer.page_speed_analyzer",
        "description": "Test your page speed for SEO performance.",
        "category": "Website Tracking Tools"
    },

    # -------- Keyword Tools --------
    {
        "name": "Keyword Suggestion Generator",
        "endpoint": "keyword_suggestion_generator.keyword_suggestion_generator",
        "description": "Get keyword ideas based on real search data.",
        "category": "Keyword Tools"
    },
    {
        "name": "Keyword Density Analyzer",
        "endpoint": "keyword_density_analyzer.keyword_density_analyzer",
        "description": "Analyze and visualize keyword density on any page.",
        "category": "Keyword Tools"
    },
    
   
    {
        "name": "LSI Keyword Generator",
        "endpoint": "lsi_keyword_generator.lsi_keyword_generator",
        "description": "Generate semantically related keywords (LSI) for content.",
        "category": "Keyword Tools"
    },

    # -------- Backlink Tools --------
    {
        "name": "Anchor Text Checker",
        "endpoint": "anchor_text_checker.anchor_text_checker",
        "description": "See anchor text distribution for link profiles.",
        "category": "Backlink Tools"
    },
    {
        "name": "Broken Backlink Finder",
        "endpoint": "broken_backlink_finder.broken_backlink_finder",
        "description": "Find backlinks pointing to broken pages.",
        "category": "Backlink Tools"
    },
    {
        "name": "Referring Domain Analyzer",
        "endpoint": "referring_domain_analyzer.referring_domain_analyzer",
        "description": "Analyze and list all referring domains.",
        "category": "Backlink Tools"
    },    
    {
        "name": "Link Status Monitor",
        "endpoint": "link_status_monitor.link_status_monitor",
        "description": "Check HTTP status of multiple URLs in bulk.",
        "category": "Backlink Tools"
    },
    {
        "name": "Backlink URL Monitor",
        "endpoint": "backlink_url_monitor.backlink_url_monitor",
        "description": "Check if specific pages are still linking to your website.",
        "category": "Backlink Tools"
    },
    {
        "name": "Internal Link Analyzer",
        "endpoint": "internal_link_analyzer.internal_link_analyzer",
        "description": "Analyze internal links on any webpage.",
        "category": "Backlink Tools"
    },
    {
        "name": "Link Profile Analyzer",
        "endpoint": "link_profile_analyzer.link_profile_analyzer",
        "description": "AnaAnalyze internal and external links on any webpage.",
        "category": "Backlink Tools"
    },
    {
        "name": "Internal Link Structure Analyzer",
        "endpoint": "internal_link_structure_analyzer.internal_link_structure",
        "description": "Visualize internal link relationships on any webpage.",
        "category": "Backlink Tools"
    },

    # -------- Image Editing Tools --------
    {
        "name": "Image Alt Text Checker",
        "endpoint": "image_alt_text_checker.image_alt_text_checker",
        "description": "Audit image alt tags for SEO and accessibility.",
        "category": "Image Editing Tools"
    },
    {
        "name": "Image Compressor",
        "endpoint": "image_compressor.image_compressor",
        "description": "Compress images for faster website loading.",
        "category": "Image Editing Tools"
    },
    {
        "name": "Image to WebP Converter",
        "endpoint": "image_to_webp_converter.image_to_webp_converter",
        "description": "Convert images to WebP format for web performance.",
        "category": "Image Editing Tools"
    },
    {
        "name": "Image Dimension Checker",
        "endpoint": "image_dimension_checker.image_dimension_checker",
        "description": "Check image dimensions, format, and aspect ratio.",
        "category": "Image Editing Tools"
    },

    # -------- Domain Tools --------
    
    {
        "name": "Expiry Date Checker",
        "endpoint": "expiry_date_checker.expiry_date_checker",
        "description": "Check domain expiry/renewal date from WHOIS.",
        "category": "Domain Tools"
    },
    {
        "name": "Whois Lookup",
        "endpoint": "whois_lookup.whois_lookup",
        "description": "Get full WHOIS info for any domain name.",
        "category": "Domain Tools"
    },
    {
        "name": "DNS Lookup",
        "endpoint": "dns_lookup.dns_lookup",
        "description": "Check A, MX, TXT, NS, and other DNS records.",
        "category": "Domain Tools"
    },
    {
        "name": "Reverse IP Lookup",
        "endpoint": "reverse_ip_lookup.reverse_ip_lookup",
        "description": "See all domains hosted on the same IP address.",
        "category": "Domain Tools"
    },

    # -------- Password Management Tools --------
    {
        "name": "Password Generator",
        "endpoint": "password_generator.password_generator",
        "description": "Generate secure, random passwords instantly.",
        "category": "Password Management Tools"
    },
    {
        "name": "Password Strength Checker",
        "endpoint": "password_strength_checker.password_strength_checker",
        "description": "Test the strength of any password in real time.",
        "category": "Password Management Tools"
    },

    # -------- Online PDF Tools --------
    {
        "name": "PDF to Text Extractor",
        "endpoint": "pdf_to_text_extractor.pdf_to_text_extractor",
        "description": "Extract text from any PDF instantly.",
        "category": "Online PDF Tools"
    },
    {
        "name": "PDF Compressor",
        "endpoint": "pdf_compressor.pdf_compressor",
        "description": "Compress large PDF files for easier sharing.",
        "category": "Online PDF Tools"
    },
    {
        "name": "PDF Metadata Viewer",
        "endpoint": "pdf_metadata_viewer.pdf_metadata_viewer",
        "description": "View hidden metadata inside PDF files.",
        "category": "Online PDF Tools"
    },

    # -------- Development Tools --------
    {
        "name": "JSON-LD Validator",
        "endpoint": "json_ld_validator.json_ld_validator",
        "description": "Validate your JSON-LD code for SEO/schema.",
        "category": "Development Tools"
    },
    {
        "name": "Schema Markup Tester",
        "endpoint": "schema_markup_tester.schema_markup_tester",
        "description": "Test and preview any page’s schema markup.",
        "category": "Development Tools"
    },
    {
        "name": "AMP Validator",
        "endpoint": "amp_validator.amp_validator",
        "description": "Check AMP (Accelerated Mobile Pages) validity.",
        "category": "Development Tools"
    },
    
    {
        "name": "FAQ Schema Generator",
        "endpoint": "faq_schema_generator.faq_schema_generator",
        "description": "Create FAQPage schema for rich Google results.",
        "category": "Development Tools"
    },
    {
        "name": "JavaScript Obfuscator",
        "endpoint": "javascript_obfuscator.js_obfuscator",
        "description": "Protect your JavaScript code with our fast server-side JS obfuscator tool.",
        "category": "Development Tools"
    },
    
    {
        "name": "JavaScript Code Beautifier",
        "endpoint": "javascript_beautifier.js_beautifier",
        "description": "Format and beautify your JavaScript code for better readability.",
        "category": "Development Tools"
    },
    
    {
        "name": "JavaScript Minifier",
        "endpoint": "javascript_minifier.js_minifier",
        "description": "Minify your JavaScript code for faster performance and smaller file size.",
        "category": "Development Tools"
    },
    {
        "name": "Mobile Optimization Tester",
        "endpoint": "mobile_tester.mobile_tester",
        "description": "MinTest your webpage for mobile responsiveness, viewport, font size, and user-friendliness.",
        "category": "Development Tools"
    },
    {
        "name": "SEO Audit Tool",
        "endpoint": "seo_audit_tool.seo_audit",
        "description": "Run a quick SEO audit of your webpage.",
        "category": "Development Tools"
    },
    {
        "name": "Code Linter",
        "endpoint": "code_linter.code_linter",
        "description": "Lint your HTML, CSS, or JavaScript code to check for common errors and formatting issues.",
        "category": "Development Tools"
    },
    {
        "name": "HTTP Header Checker",
        "endpoint": "http_header_checker.http_header_checker",
        "description": "View HTTP response headers for any URL.",
        "category": "Development Tools"
    },
    {
        "name": "JavaScript Error Logger",
        "endpoint": "js_error_logger.js_error_logger",
        "description": "Find and debug runtime errors in JavaScript code using a safe sandbox environment.",
        "category": "Development Tools"
    },
    {
        "name": "CSS & JS Bundler",
        "endpoint": "css_js_bundler.css_js_bundler",
        "description": "Combine and minify multiple CSS or JavaScript files instantly.",
        "category": "Development Tools"
    },
    {
        "name": "Sitemap Generator",
        "endpoint": "sitemap_generator.sitemap_generator",
        "description": "Generate XML sitemap for any website to improve indexing and SEO visibility.",
        "category": "Development Tools"
    },
    {
        "name": "HTML Minifier",
        "endpoint": "html_minifier.html_minifier",
        "description": "Minify HTML code by removing comments, line breaks, and extra spaces.",
        "category": "Development Tools"
    },
    {
        "name": "Robots.txt Generator",
        "endpoint": "robots_generator.robots_generator",
        "description": "Generate a perfect robots.txt file to control how search engines crawl your website.",
        "category": "Development Tools"
    },
    {
        "name": "Website Speed Test",
        "endpoint": "speed_test.speed_test",
        "description": "Check website load time, page size, and resource stats using our custom speed tester.",
        "category": "Development Tools"
    },
   

# -------- Meta Tags Tools --------
    {
        "name": "Meta Description Generator",
        "endpoint": "meta_description_generator.meta_description_generator",
        "description": "Create optimized meta descriptions for any page.",
        "category": "Meta Tags Tools"
    },
    

# -------- Content & Readability Tools --------
    
    {
        "name": "Readability Checker",
        "endpoint": "readability_checker.readability_checker",
        "description": "Analyze text for Flesch score and grade level.",
        "category": "Text Analysis Tools"
    },


    
    
    # -------- Website Tracking Tools --------
    
    {
        "name": "Referrer IP Tracker",
        "endpoint": "referrer_ip_tracker.referrer_ip_tracker",  # blueprint_name.endpoint_function_name
        "description": "Track visitor IP and referrer info easily.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Request Rate Monitor",
        "endpoint": "request_rate_monitor.request_rate_monitor",  # blueprint_name.endpoint_function_name
        "description": "Track how many requests your IP has sent.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Referrer Log Analyzer",
        "endpoint": "referrer_log_analyzer.referrer_log_analyzer",  # blueprint_name.endpoint_function_name
        "description": "Upload your referrer log and analyze top referring domains and suspicious sources.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Click Fraud Detector",
        "endpoint": "click_fraud_detector.click_fraud_detector",  # blueprint_name.endpoint_function_name
        "description": "Upload your click logs and detect suspicious repeated clicks.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Referrer Spam Filter",
        "endpoint": "referrer_spam_filter.referrer_spam_filter",  # blueprint_name.endpoint_function_name
        "description": "Filter out spammy referrer domains from your traffic.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Conversion Funnel Tracker",
        "endpoint": "conversion_funnel_tracker.conversion_funnel_tracker",  # blueprint_name.endpoint_function_name
        "description": "Upload user funnel logs to analyze conversion rates and drop-offs in.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Uptime Monitor",
        "endpoint": "uptime_monitor.uptime_monitor",  # blueprint_name.endpoint_function_name
        "description": "Check website uptime, HTTP status, and response time instantly.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Bot Detector",
        "endpoint": "bot_detection.bot_detection",  # blueprint_name.endpoint_function_name
        "description": "Detect if a User-Agent string belongs to a bot or crawler instantly.",
        "category": "Website Tracking Tools"
    },
    {
        "name": "Page View Counter",
        "endpoint": "page_view_counter.page_view_counter",  # blueprint_name.endpoint_function_name
        "description": "Track page views by URL or page slug.",
        "category": "Website Tracking Tools"
    },
    
    # -------- AI Writing Generator    --------
    {
        "name": "Blog Outline Generator",
        "endpoint": "blog_outline_generator.blog_outline_generator",
        "description": "Generate SEO-focused blog outlines using AI.",
        "category": "AI Writing Generators"
    },
    
    {
        "name": "Text Summarizer",
        "endpoint": "text_summarizer.text_summarizer",
        "description": "Summarize long articles or paragraphs instantly.",
        "category": "AI Writing Generators"
    },
    
    {
        "name": "Writing Style Analyzer",
        "endpoint": "writing_style_analyzer.writing_style_analyzer",
        "description": "Analyze your writing style, readability, and sentence structure.",
        "category": "AI Writing Generators"
    },
    {
        "name": "Headline Generator",
        "endpoint": "headline_generator.headline_generator",  # blueprint name . function name
        "description": "Generate catchy, SEO-friendly headlines.",
        "category": "AI Writing Generators"
    },
    {
        "name": "AI Content Generator Basic",
        "endpoint": "ai_content_generator_basic.ai_content_generator",
        "description": "Generate clear, SEO-friendly content on any topic instantly with AI.",
        "category": "AI Writing Generators"
    },
    {
        "name": "Auto Title Generator",
        "endpoint": "auto_title_generator.auto_title_generator",
        "description": "Generate clear, SEO-friendly Title on any topic instantly with AI.",
        "category": "AI Writing Generators"
    },
    {
        "name": "Grammar Checker",
        "endpoint": "grammar_checker.grammar_checker",
        "description": "Use AI to professionally rewrite content for clarity, SEO, and engagement.",
        "category": "AI Writing Generators"
    },
    {
        "name": "Content Rewriter Pro",
        "endpoint": "content_rewriter_pro.content_rewriter_pro",
        "description": "Check grammar using our AI-powered grammar correction tool.",
        "category": "AI Writing Generators"
    },
    {
        "name": "Text Summarizer Pro",
        "endpoint": "text_summarizer_pro.text_summarizer_pro",
        "description": "Generate high-quality summaries of any content using our professional AI-powered text summarizer.",
        "category": "AI Writing Generators"
    },
    {
        "name": "Title Tag Generator",
        "endpoint": "title_tag_generator.title_tag_generator",
        "description": "Generate SEO-optimized title tags for any topic.",
        "category": "AI Writing Generators"
    },
    {
        "name": "SEO Score Calculator",
        "endpoint": "seo_score_calculator.seo_score_calculator",
        "description": "Get a real-time SEO score and improvement tips for your content using AI.",
        "category": "AI Writing Generators"
    },
    {
        "name": "Content Enhancer",
        "endpoint": "content_enhancer.content_enhancer",
        "description": "Improve your content’s tone, clarity, and engagement with our AI-powered Content Enhancer tool.",
        "category": "AI Writing Generators"
    },
    {
        "name": "Paraphrasing Tool",
        "endpoint": "paraphrasing_tool.paraphrasing_tool",
        "description": "Rewrite your content in a unique and human-like way using our AI-powered Paraphrasing Tool",
        "category": "AI Writing Generators"
    },
    
    
   
    
]

@tools_bp.route('/', endpoint='list_tools')
def list_tools():
    return render_template("tools/list.html", tools=all_tools)

@tools_bp.route('/category/<category_slug>', endpoint='category_page')
def category_page(category_slug):
    filtered = [
        tool for tool in all_tools
        if tool['category'].lower().replace(" ", "-") == category_slug.lower()
    ]
    display_name = category_slug.replace("-", " ").title()
    return render_template("tools/category_page.html", tools=filtered, category=display_name)

def register_tool_blueprints(app):
    app.register_blueprint(meta_tag_analyzer_bp)
    app.register_blueprint(open_graph_preview_bp)
    app.register_blueprint(serp_snippet_preview_bp)
    
    app.register_blueprint(broken_link_checker_bp)
    app.register_blueprint(redirect_checker_bp)
   
    app.register_blueprint(find_all_links_bp)
    app.register_blueprint(favicon_checker_bp)
    app.register_blueprint(ssl_checker_bp)
    app.register_blueprint(http_header_checker_bp)
    app.register_blueprint(crawlability_tester_bp)
    
    
    
    app.register_blueprint(utm_builder_bp)
    app.register_blueprint(ip_location_finder_bp)
    app.register_blueprint(page_speed_analyzer_bp)
    app.register_blueprint(keyword_suggestion_generator_bp)
    app.register_blueprint(keyword_density_analyzer_bp)
    
    
    app.register_blueprint(lsi_keyword_generator_bp)
    app.register_blueprint(anchor_text_checker_bp)
    app.register_blueprint(broken_backlink_finder_bp)
    app.register_blueprint(referring_domain_analyzer_bp)
    app.register_blueprint(meta_tag_generator_bp)
    app.register_blueprint(robots_txt_tester_bp)
    app.register_blueprint(sitemap_xml_validator_bp)
    app.register_blueprint(hreflang_tag_checker_bp)
    app.register_blueprint(canonical_tag_checker_bp)
    app.register_blueprint(image_alt_text_checker_bp)
    app.register_blueprint(image_compressor_bp)
    app.register_blueprint(image_to_webp_converter_bp)
    app.register_blueprint(image_dimension_checker_bp)
    
    app.register_blueprint(expiry_date_checker_bp)
    app.register_blueprint(whois_lookup_bp)
    app.register_blueprint(dns_lookup_bp)
    app.register_blueprint(reverse_ip_lookup_bp)
    app.register_blueprint(password_generator_bp)
    app.register_blueprint(password_strength_checker_bp)
    app.register_blueprint(pdf_to_text_extractor_bp)
    app.register_blueprint(pdf_compressor_bp)
    app.register_blueprint(pdf_metadata_viewer_bp)
    app.register_blueprint(json_ld_validator_bp)
    app.register_blueprint(schema_markup_tester_bp)
    app.register_blueprint(amp_validator_bp)
    app.register_blueprint(blog_outline_generator_bp)
   
    app.register_blueprint(faq_schema_generator_bp)
    
    app.register_blueprint(meta_description_generator_bp)
    
    app.register_blueprint(readability_checker_bp)
    app.register_blueprint(text_summarizer_bp)
    app.register_blueprint(title_tag_generator_bp)
    
    app.register_blueprint(referrer_ip_tracker_bp)
    app.register_blueprint(request_rate_monitor_bp)
    app.register_blueprint(referrer_log_analyzer_bp)
    app.register_blueprint(click_fraud_detector_bp)
    app.register_blueprint(referrer_spam_filter_bp)
    app.register_blueprint(conversion_funnel_tracker_bp)
    app.register_blueprint(uptime_monitor_bp)
    app.register_blueprint(bot_detection_bp)
    app.register_blueprint(page_view_counter_bp)
    app.register_blueprint(writing_style_analyzer_bp)
    app.register_blueprint(headline_generator_bp)
    app.register_blueprint(ai_content_generator_basic_bp)
    app.register_blueprint(auto_title_generator_bp)
    app.register_blueprint(grammar_checker_bp)
    app.register_blueprint(content_rewriter_pro_bp)
    app.register_blueprint(text_summarizer_pro_bp)
    app.register_blueprint(seo_score_calculator_bp)
    app.register_blueprint(content_enhancer_bp)
    app.register_blueprint(paraphrasing_tool_bp)
    
    app.register_blueprint(link_status_monitor_bp)
    app.register_blueprint(backlink_url_monitor_bp)
    app.register_blueprint(internal_link_analyzer_bp)
    app.register_blueprint(link_profile_analyzer_bp)
    app.register_blueprint(internal_link_structure_analyzer_bp)
    app.register_blueprint(js_obfuscator_bp)
    app.register_blueprint(js_beautifier_bp)
    app.register_blueprint(js_minifier_bp)
    app.register_blueprint(mobile_tester_bp)
    app.register_blueprint(seo_audit_tool_bp)
    app.register_blueprint(code_linter_bp)
    app.register_blueprint(js_error_logger_bp)
    app.register_blueprint(bundler_bp)
    app.register_blueprint(sitemap_bp)
    app.register_blueprint(html_minifier_bp)
    app.register_blueprint(robots_bp)
    app.register_blueprint(speed_test_bp)
    # new registers from here

    