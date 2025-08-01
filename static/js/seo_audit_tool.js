/**
 * SEO Audit Tool JavaScript - Complete functionality for displaying comprehensive SEO results
 */

// URL Utility Functions
const URLUtils = {
    /**
     * Clean URL by removing timestamp and cache-busting parameters
     * @param {string} url - The URL to clean
     * @returns {string} - Clean URL without timestamp parameters
     */
    cleanUrl: function (url) {
        if (!url) return url;

        // Remove common cache-busting parameters
        let cleanUrl = url.replace(/[?&]_t=\d+/g, '');
        cleanUrl = cleanUrl.replace(/[?&]timestamp=\d+/g, '');
        cleanUrl = cleanUrl.replace(/[?&]cache=\d+/g, '');
        cleanUrl = cleanUrl.replace(/[?&]v=\d+/g, '');

        // Remove trailing ? or & if they exist
        cleanUrl = cleanUrl.replace(/[?&]$/, '');

        return cleanUrl;
    },

    /**
     * Update browser URL without timestamp parameters
     * @param {string} newUrl - The new URL to set
     * @param {boolean} replace - Whether to replace current history entry
     */
    updateUrl: function (newUrl, replace = true) {
        const cleanUrl = this.cleanUrl(newUrl);
        if (cleanUrl !== window.location.href) {
            if (replace) {
                window.history.replaceState({}, document.title, cleanUrl);
            } else {
                window.history.pushState({}, document.title, cleanUrl);
            }
        }
    },

    /**
     * Smart refresh that cleans URL and preserves user experience
     */
    smartRefresh: function () {
        const cleanUrl = this.cleanUrl(window.location.href);
        if (cleanUrl !== window.location.href) {
            window.location.replace(cleanUrl);
        } else {
            window.location.reload();
        }
    }
};

class SEOAuditDisplay {
    constructor() {
        this.form = document.getElementById('seoAuditForm');
        this.loadingState = document.getElementById('loadingState');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.bindEvents();
        this.handleUrlParameter();
    }

    handleUrlParameter() {
        // Clean the current URL first
        URLUtils.updateUrl(window.location.href);

        // Check if there's a URL parameter from dashboard or other sources
        const urlParams = new URLSearchParams(window.location.search);
        const prefilledUrl = urlParams.get('url');

        if (prefilledUrl) {
            const urlInput = document.getElementById('url');
            if (urlInput) {
                // Clean and set the URL
                const cleanUrl = prefilledUrl.trim();
                urlInput.value = cleanUrl;
                urlInput.focus();

                // Optional: Auto-submit if valid URL (can be disabled)
                // if (this.isValidUrl(cleanUrl)) {
                //     this.handleSubmit(new Event('submit'));
                // }
            }
        }
    }

    isValidUrl(string) {
        try {
            new URL(string.startsWith('http') ? string : 'https://' + string);
            return true;
        } catch (_) {
            return false;
        }
    }

    bindEvents() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    handleSubmit(e) {
        e.preventDefault();

        const url = document.getElementById('url').value.trim();
        if (!url) {
            alert('Please enter a URL to analyze');
            return;
        }

        this.showLoading();
        this.submitForm(url);
    }

    showLoading() {
        this.loadingState.classList.remove('hidden');
        this.resultsContainer.classList.add('hidden');
    }

    hideLoading() {
        this.loadingState.classList.add('hidden');
    }

    submitForm(url) {
        // Remove CSRF token requirement for now to test functionality
        const formData = new FormData();
        formData.append('url', url);

        fetch('/tools/seo/api/analyze', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                this.hideLoading();

                console.log('SEO Audit Response:', data); // Debug logging

                try {
                    if (data.error) {
                        alert('Error: ' + data.error);
                    } else {
                        // Pass the entire data object since it contains all the analysis results
                        this.displayResults(data);
                        this.resultsContainer.classList.remove('hidden');
                    }
                } catch (displayError) {
                    console.error('Error displaying results:', displayError);
                    alert('Error displaying results: ' + (displayError.message || displayError));
                }
            })
            .catch(error => {
                this.hideLoading();
                console.error('Error:', error);
                // Better error handling
                let errorMessage = 'An error occurred while analyzing the website';
                if (error && error.message) {
                    errorMessage += ': ' + error.message;
                } else if (typeof error === 'string') {
                    errorMessage += ': ' + error;
                }
                alert(errorMessage);
            });
    }

    displayResults(results) {
        console.log('Displaying results with data:', results);

        if (!results) {
            console.error('No results provided to displayResults');
            return;
        }

        // Check if this is a premium analysis
        const isPremium = results.is_premium_analysis || false;

        // Always display overview for both free and premium users
        this.displayOverview(results);

        if (isPremium) {
            // Display all tabs with full data for premium users
            this.displayTechnicalSEO(results);
            this.displayContentAnalysis(results);
            this.displayPerformanceAnalysis(results);
            this.displayRecommendations(results);
            this.displayPagesAnalyzed(results);
        } else {
            // Display locked tabs for free users
            this.displayLockedTabs();
        }
    }

    displayLockedTabs() {
        // Display locked content for free users in all tabs except overview
        const lockedContent = `
            <div class="flex items-center justify-center min-h-[400px]">
                <div class="text-center max-w-md">
                    <div class="mb-6">
                        <i data-lucide="lock" class="w-16 h-16 text-blue-500 mx-auto"></i>
                    </div>
                    <h3 class="text-2xl font-bold text-gray-900 mb-3">Unlock Complete SEO Analysis</h3>
                    <p class="text-gray-600 mb-6">
                        Get access to comprehensive SEO analysis including technical audits, 
                        content analysis, performance insights, and detailed recommendations.
                    </p>
                    <div class="space-y-3 mb-6">
                        <div class="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 p-4 rounded-lg text-sm">
                            <div class="flex items-center">
                                <i data-lucide="check-circle" class="w-5 h-5 text-green-600 mr-3"></i>
                                <span class="text-gray-800 font-medium">500+ page deep crawl analysis</span>
                            </div>
                        </div>
                        <div class="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 p-4 rounded-lg text-sm">
                            <div class="flex items-center">
                                <i data-lucide="check-circle" class="w-5 h-5 text-green-600 mr-3"></i>
                                <span class="text-gray-800 font-medium">Advanced technical SEO checks</span>
                            </div>
                        </div>
                        <div class="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 p-4 rounded-lg text-sm">
                            <div class="flex items-center">
                                <i data-lucide="check-circle" class="w-5 h-5 text-green-600 mr-3"></i>
                                <span class="text-gray-800 font-medium">Competitor analysis & insights</span>
                            </div>
                        </div>
                        <div class="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 p-4 rounded-lg text-sm">
                            <div class="flex items-center">
                                <i data-lucide="check-circle" class="w-5 h-5 text-green-600 mr-3"></i>
                                <span class="text-gray-800 font-medium">Detailed actionable recommendations</span>
                            </div>
                        </div>
                        <div class="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 p-4 rounded-lg text-sm">
                            <div class="flex items-center">
                                <i data-lucide="star" class="w-5 h-5 text-orange-600 mr-3"></i>
                                <span class="text-gray-800 font-medium">$100 worth of analysis for just $29</span>
                            </div>
                        </div>
                    </div>
                    <div class="space-y-3">
                        <a href="/pricing" class="inline-block w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105">
                            Upgrade to Pro - $29/month
                        </a>
                        <a href="/pricing" class="inline-block text-blue-600 hover:text-blue-800 text-sm font-medium">
                            View all Pro features →
                        </a>
                    </div>
                    <p class="text-sm text-gray-500 mt-4">No commitment • Cancel anytime • 7-day free trial</p>
                </div>
            </div>
        `;

        // Set locked content for all tabs except overview
        const tabIds = ['technical_content', 'content_content', 'performance_content', 'recommendations_content', 'pages_content'];

        tabIds.forEach(tabId => {
            const element = document.getElementById(tabId);
            if (element) {
                element.innerHTML = lockedContent;
            }
        });
    }

    displayLimitedTechnicalSEO(results) {
        // Show limited technical SEO with upgrade prompt
        const html = `
            <div class="space-y-6">
                <!-- Basic Technical Factors -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="font-semibold mb-4">Basic Technical Factors</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
                            <span>HTTPS Usage</span>
                            <span class="flex items-center ${results.technical_analysis?.https_usage?.uses_https ? 'text-green-600' : 'text-red-600'}">
                                <i data-lucide="${results.technical_analysis?.https_usage?.uses_https ? 'check' : 'x'}" class="w-4 h-4 mr-1"></i>
                                ${results.technical_analysis?.https_usage?.uses_https ? 'Secure' : 'Not Secure'}
                            </span>
                        </div>
                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
                            <span>Robots.txt</span>
                            <span class="flex items-center ${results.robots_txt?.exists ? 'text-green-600' : 'text-orange-600'}">
                                <i data-lucide="${results.robots_txt?.exists ? 'check' : 'alert-triangle'}" class="w-4 h-4 mr-1"></i>
                                ${results.robots_txt?.exists ? 'Found' : 'Missing'}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Premium Features Locked -->
                <div class="bg-gradient-to-r from-orange-100 to-red-100 border border-orange-200 rounded-lg p-6">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <i data-lucide="lock" class="w-8 h-8 text-orange-600 mr-4"></i>
                            <div>
                                <h4 class="font-semibold text-gray-900 mb-1">Advanced Technical Analysis</h4>
                                <p class="text-gray-600 text-sm">Unlock 50+ technical SEO checks including:</p>
                                <ul class="text-sm text-gray-600 mt-2 space-y-1">
                                    <li>• SSL Certificate Analysis</li>
                                    <li>• Security Headers Check</li>
                                    <li>• CDN Configuration</li>
                                    <li>• Server Response Analysis</li>
                                    <li>• JavaScript/CSS Optimization</li>
                                </ul>
                            </div>
                        </div>
                        <a href="/pricing" class="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold">
                            Upgrade to Pro
                        </a>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('technical_content').innerHTML = html;
    }

    displayUpgradePrompts(results) {
        // Display upgrade prompts throughout the interface

        // Add upgrade banners to various sections
        const upgradePrompts = `
            <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-lg mb-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <i data-lucide="star" class="w-8 h-8 mr-4"></i>
                        <div>
                            <h3 class="text-xl font-bold mb-1">Unlock Complete SEO Analysis</h3>
                            <p class="text-blue-100">Get 500+ page analysis, competitor insights, and detailed recommendations</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div class="text-right">
                            <div class="text-2xl font-bold">$29</div>
                            <div class="text-blue-200 text-sm">per month</div>
                        </div>
                        <a href="/pricing" class="bg-white text-blue-600 hover:bg-gray-100 px-6 py-3 rounded-lg font-semibold">
                            Start Pro Trial
                        </a>
                    </div>
                </div>
            </div>
        `;

        // Insert upgrade prompt after overview
        const overviewContent = document.getElementById('overview_content');
        if (overviewContent) {
            overviewContent.insertAdjacentHTML('beforeend', upgradePrompts);
        }
    }

    displayOverview(results) {
        console.log('displayOverview called with:', results);

        const seoScore = results.overall_score || 0;
        const scoreColor = seoScore >= 80 ? 'green' : seoScore >= 60 ? 'yellow' : 'red';
        const scoreGrade = this.getScoreGrade(seoScore);
        const reportId = results.report_id || null;

        const html = `
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <!-- SEO Score Card -->
                <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-lg relative overflow-hidden">
                    <div class="relative z-10">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-blue-100">Overall SEO Score</p>
                                <div class="flex items-baseline">
                                    <p class="text-4xl font-bold">${seoScore}</p>
                                    <p class="text-2xl ml-1">/100</p>
                                    <span class="ml-3 px-2 py-1 bg-white bg-opacity-20 rounded text-sm font-medium">${scoreGrade}</span>
                                </div>
                            </div>
                            <div class="relative">
                                <div class="w-16 h-16 rounded-full border-4 border-white border-opacity-30 flex items-center justify-center">
                                    <span class="text-xl font-bold">${scoreGrade}</span>
                                </div>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="w-full bg-white bg-opacity-20 rounded-full h-2">
                                <div class="bg-white h-2 rounded-full transition-all duration-500" style="width: ${seoScore}%"></div>
                            </div>
                        </div>
                    </div>
                    <div class="absolute -right-4 -top-4 w-24 h-24 bg-white bg-opacity-10 rounded-full"></div>
                </div>
                
                <!-- Pages Crawled Card -->
                <div class="bg-gradient-to-r from-green-500 to-teal-600 text-white p-6 rounded-lg">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-green-100">Pages Analyzed</p>
                            <p class="text-3xl font-bold">${results.crawl_summary?.successfully_crawled || 1}</p>
                            <p class="text-sm text-green-100 mt-1">
                                ${results.crawl_summary?.total_pages_found || 1} pages found
                            </p>
                        </div>
                        <i data-lucide="file-text" class="w-8 h-8"></i>
                    </div>
                </div>
                
                <!-- Issues Card -->
                <div class="bg-gradient-to-r from-orange-500 to-red-600 text-white p-6 rounded-lg">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-orange-100">Issues Found</p>
                            <p class="text-3xl font-bold">${this.countIssues(results)}</p>
                            <div class="flex text-sm text-orange-100 mt-1 space-x-2">
                                <span>${this.countCriticalIssues(results)} Critical</span>
                                <span>•</span>
                                <span>${this.countWarningIssues(results)} Warnings</span>
                            </div>
                        </div>
                        <i data-lucide="alert-triangle" class="w-8 h-8"></i>
                    </div>
                </div>
            </div>

            <!-- Detailed Score Breakdown -->
            <div class="bg-white p-6 rounded-lg border border-gray-200 mb-6">
                <h4 class="text-lg font-semibold mb-4 flex items-center">
                    <i data-lucide="bar-chart-3" class="w-5 h-5 mr-2"></i>
                    Score Breakdown
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    ${this.generateScoreBreakdown(results)}
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Crawl Summary -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4">Crawl Summary</h4>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Total Pages Found:</span>
                            <span class="font-medium">${results.crawl_summary?.total_pages_found || 1}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Successfully Crawled:</span>
                            <span class="font-medium text-green-600">${results.crawl_summary?.successfully_crawled || 1}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Failed Pages:</span>
                            <span class="font-medium text-red-600">${results.crawl_summary?.failed_pages || 0}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Crawl Depth:</span>
                            <span class="font-medium">${results.crawl_summary?.crawl_depth || 5}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Audit Duration:</span>
                            <span class="font-medium">${results.total_audit_time || 0}s</span>
                        </div>
                    </div>
                </div>

                <!-- Quick Insights -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4">Quick Insights</h4>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Robots.txt:</span>
                            <span class="font-medium ${results.robots_txt?.exists ? 'text-green-600' : 'text-red-600'}">
                                ${results.robots_txt?.exists ? 'Found' : 'Missing'}
                            </span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Sitemap:</span>
                            <span class="font-medium ${results.sitemap?.found ? 'text-green-600' : 'text-red-600'}">
                                ${results.sitemap?.found ? 'Found' : 'Missing'}
                            </span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">HTTPS Usage:</span>
                            <span class="font-medium">${results.technical_analysis?.https_usage?.https_percentage || 0}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Schema Markup:</span>
                            <span class="font-medium">${results.technical_analysis?.structured_data?.schema_percentage || 0}%</span>
                        </div>
                    </div>
                </div>
            </div>

            ${reportId ? `
            <!-- Report Actions -->
            <div class="bg-blue-50 border border-blue-200 p-4 rounded-lg mt-6">
                <div class="flex items-center justify-between">
                    <div>
                        <h5 class="font-medium text-blue-800">Report Saved Successfully!</h5>
                        <p class="text-sm text-blue-600">Your SEO audit has been saved to your dashboard.</p>
                    </div>
                    <div class="flex space-x-2">
                        <a href="/tools/seo-report/${reportId}" 
                           class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                            View Full Report
                        </a>
                        <a href="/tools/seo-report/${reportId}/pdf" 
                           class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm">
                            Download PDF
                        </a>
                    </div>
                </div>
            </div>
            ` : ''}
        `;

        document.getElementById('overview_content').innerHTML = html;
        console.log('displayOverview completed successfully');
    }

    displayTechnicalSEO(results) {
        const technical = results.technical_analysis || {};
        const siteWide = results.site_wide_issues || {};
        const robots = results.robots_txt || {};
        const sitemap = results.sitemap || {};

        const html = `
            <div class="space-y-6">
                <!-- HTTPS Security -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="shield" class="w-5 h-5 mr-2"></i>
                        HTTPS Security
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <p class="text-gray-600">HTTPS Pages:</p>
                            <p class="text-xl font-bold text-${technical.https_usage?.https_percentage >= 100 ? 'green' : 'red'}-600">
                                ${technical.https_usage?.total_https_pages || 0} / ${results.crawl_summary?.successfully_crawled || 1}
                            </p>
                        </div>
                        <div>
                            <p class="text-gray-600">HTTPS Coverage:</p>
                            <p class="text-xl font-bold text-${technical.https_usage?.https_percentage >= 100 ? 'green' : 'red'}-600">
                                ${technical.https_usage?.https_percentage || 0}%
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Canonical Tags -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="link" class="w-5 h-5 mr-2"></i>
                        Canonical Tags
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <p class="text-gray-600">Pages with Canonical:</p>
                            <p class="text-xl font-bold">${technical.canonical_tags?.pages_with_canonical || 0}</p>
                        </div>
                        <div>
                            <p class="text-gray-600">Coverage:</p>
                            <p class="text-xl font-bold text-${technical.canonical_tags?.canonical_percentage >= 80 ? 'green' : 'yellow'}-600">
                                ${technical.canonical_tags?.canonical_percentage || 0}%
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Structured Data -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="code" class="w-5 h-5 mr-2"></i>
                        Structured Data (Schema Markup)
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <p class="text-gray-600">Pages with Schema:</p>
                            <p class="text-xl font-bold">${technical.structured_data?.pages_with_schema || 0}</p>
                        </div>
                        <div>
                            <p class="text-gray-600">Coverage:</p>
                            <p class="text-xl font-bold text-${technical.structured_data?.schema_percentage >= 50 ? 'green' : 'yellow'}-600">
                                ${technical.structured_data?.schema_percentage || 0}%
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Robots.txt Analysis -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="file-text" class="w-5 h-5 mr-2"></i>
                        Robots.txt Analysis
                    </h4>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Status:</span>
                            <span class="font-medium text-${robots.exists ? 'green' : 'red'}-600">
                                ${robots.exists ? 'Found' : 'Missing'}
                            </span>
                        </div>
                        ${robots.exists ? `
                            <div class="flex justify-between">
                                <span class="text-gray-600">Disallow Rules:</span>
                                <span class="font-medium">${robots.disallow_patterns?.length || 0}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Sitemaps Listed:</span>
                                <span class="font-medium">${robots.sitemaps?.length || 0}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>

                <!-- Sitemap Analysis -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="map" class="w-5 h-5 mr-2"></i>
                        Sitemap Analysis
                    </h4>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Status:</span>
                            <span class="font-medium text-${sitemap.found ? 'green' : 'red'}-600">
                                ${sitemap.found ? 'Found' : 'Missing'}
                            </span>
                        </div>
                        ${sitemap.found ? `
                            <div class="flex justify-between">
                                <span class="text-gray-600">Total URLs:</span>
                                <span class="font-medium">${sitemap.total_urls || 0}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Valid URLs:</span>
                                <span class="font-medium text-green-600">${sitemap.valid_urls || 0}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>

                <!-- Duplicate Content Issues -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="copy" class="w-5 h-5 mr-2"></i>
                        Duplicate Content Issues
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <p class="text-gray-600">Duplicate Titles:</p>
                            <p class="text-xl font-bold text-${Object.keys(siteWide.duplicate_titles || {}).length > 0 ? 'red' : 'green'}-600">
                                ${Object.keys(siteWide.duplicate_titles || {}).length}
                            </p>
                        </div>
                        <div>
                            <p class="text-gray-600">Duplicate Meta Descriptions:</p>
                            <p class="text-xl font-bold text-${Object.keys(siteWide.duplicate_meta_descriptions || {}).length > 0 ? 'red' : 'green'}-600">
                                ${Object.keys(siteWide.duplicate_meta_descriptions || {}).length}
                            </p>
                        </div>
                        <div>
                            <p class="text-gray-600">Duplicate H1 Tags:</p>
                            <p class="text-xl font-bold text-${Object.keys(siteWide.duplicate_h1_tags || {}).length > 0 ? 'red' : 'green'}-600">
                                ${Object.keys(siteWide.duplicate_h1_tags || {}).length}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('technical_content').innerHTML = html;
    }

    displayContentAnalysis(results) {
        const pages = results.pages_analysis?.pages || {};
        const aggregateStats = results.pages_analysis?.aggregate_stats || {};

        // Get first page data for detailed analysis
        const firstPageUrl = Object.keys(pages)[0];
        const firstPage = firstPageUrl ? pages[firstPageUrl] : null;

        const html = `
            <div class="space-y-6">
                <!-- Aggregate Content Statistics -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="type" class="w-5 h-5 mr-2"></i>
                        Content Overview
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div class="text-center">
                            <p class="text-gray-600">Avg Title Length</p>
                            <p class="text-xl font-bold">${aggregateStats.avg_title_length || 0} chars</p>
                        </div>
                        <div class="text-center">
                            <p class="text-gray-600">Avg Meta Description</p>
                            <p class="text-xl font-bold">${aggregateStats.avg_meta_description_length || 0} chars</p>
                        </div>
                        <div class="text-center">
                            <p class="text-gray-600">Missing Titles</p>
                            <p class="text-xl font-bold text-${aggregateStats.pages_missing_title > 0 ? 'red' : 'green'}-600">
                                ${aggregateStats.pages_missing_title || 0}
                            </p>
                        </div>
                        <div class="text-center">
                            <p class="text-gray-600">Missing Meta Desc</p>
                            <p class="text-xl font-bold text-${aggregateStats.pages_missing_meta_description > 0 ? 'red' : 'green'}-600">
                                ${aggregateStats.pages_missing_meta_description || 0}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Image Analysis -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="image" class="w-5 h-5 mr-2"></i>
                        Image Analysis
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="text-center">
                            <p class="text-gray-600">Total Images</p>
                            <p class="text-xl font-bold">${aggregateStats.total_images || 0}</p>
                        </div>
                        <div class="text-center">
                            <p class="text-gray-600">Missing Alt Text</p>
                            <p class="text-xl font-bold text-${aggregateStats.images_missing_alt > 0 ? 'red' : 'green'}-600">
                                ${aggregateStats.images_missing_alt || 0}
                            </p>
                        </div>
                        <div class="text-center">
                            <p class="text-gray-600">Alt Text Coverage</p>
                            <p class="text-xl font-bold text-${this.calculateAltCoverage(aggregateStats) >= 90 ? 'green' : 'yellow'}-600">
                                ${this.calculateAltCoverage(aggregateStats)}%
                            </p>
                        </div>
                    </div>
                </div>

                ${firstPage ? `
                <!-- Sample Page Analysis -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="file-text" class="w-5 h-5 mr-2"></i>
                        Sample Page Analysis
                    </h4>
                    <p class="text-sm text-gray-600 mb-4">Analysis of: ${firstPageUrl}</p>
                    
                    <div class="space-y-4">
                        <!-- Title Analysis -->
                        <div class="border-l-4 border-${this.getTitleStatus(firstPage.title)} pl-4">
                            <h5 class="font-medium">Title Tag</h5>
                            <p class="text-sm text-gray-600">${firstPage.title?.text || 'Missing'}</p>
                            <p class="text-xs text-gray-500">Length: ${firstPage.title?.length || 0} characters</p>
                        </div>

                        <!-- Meta Description -->
                        <div class="border-l-4 border-${this.getMetaStatus(firstPage.meta?.description)} pl-4">
                            <h5 class="font-medium">Meta Description</h5>
                            <p class="text-sm text-gray-600">${firstPage.meta?.description?.text || 'Missing'}</p>
                            <p class="text-xs text-gray-500">Length: ${firstPage.meta?.description?.length || 0} characters</p>
                        </div>

                        <!-- Headings Structure -->
                        <div class="border-l-4 border-blue-500 pl-4">
                            <h5 class="font-medium">Headings Structure</h5>
                            <div class="text-sm text-gray-600">
                                <span>H1: ${firstPage.headings?.h1_count || 0}</span> |
                                <span>H2: ${firstPage.headings?.h2_count || 0}</span> |
                                <span>H3: ${firstPage.headings?.h3_count || 0}</span> |
                                <span>H4: ${firstPage.headings?.h4_count || 0}</span> |
                                <span>H5: ${firstPage.headings?.h5_count || 0}</span> |
                                <span>H6: ${firstPage.headings?.h6_count || 0}</span>
                            </div>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
        `;

        document.getElementById('content_content').innerHTML = html;
    }

    displayPerformanceAnalysis(results) {
        const aggregateStats = results.pages_analysis?.aggregate_stats || {};
        const pages = results.pages_analysis?.pages || {};

        // Get performance data from first page
        const firstPageUrl = Object.keys(pages)[0];
        const firstPage = firstPageUrl ? pages[firstPageUrl] : null;
        const performance = firstPage?.performance || {};

        const html = `
            <div class="space-y-6">
                <!-- Overall Performance -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="gauge" class="w-5 h-5 mr-2"></i>
                        Performance Overview
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="text-center">
                            <p class="text-gray-600">Avg Page Size</p>
                            <p class="text-xl font-bold">${aggregateStats.avg_page_size || 0} KB</p>
                        </div>
                        <div class="text-center">
                            <p class="text-gray-600">Avg Load Time</p>
                            <p class="text-xl font-bold">${aggregateStats.avg_load_time || 0}s</p>
                        </div>
                        <div class="text-center">
                            <p class="text-gray-600">Performance Score</p>
                            <p class="text-xl font-bold text-${this.getPerformanceColor(performance.score)}-600">
                                ${performance.score || 0}/100
                            </p>
                        </div>
                    </div>
                </div>

                ${firstPage ? `
                <!-- Sample Page Performance -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="clock" class="w-5 h-5 mr-2"></i>
                        Sample Page Performance
                    </h4>
                    <p class="text-sm text-gray-600 mb-4">Performance of: ${firstPageUrl}</p>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div>
                            <p class="text-gray-600">Load Time</p>
                            <p class="text-lg font-bold">${performance.load_time || 0}s</p>
                        </div>
                        <div>
                            <p class="text-gray-600">Content Size</p>
                            <p class="text-lg font-bold">${Math.round((performance.content_size || 0) / 1024)} KB</p>
                        </div>
                        <div>
                            <p class="text-gray-600">Response Time</p>
                            <p class="text-lg font-bold">${performance.response_time || 0}ms</p>
                        </div>
                        <div>
                            <p class="text-gray-600">Status Code</p>
                            <p class="text-lg font-bold text-${performance.status_code === 200 ? 'green' : 'red'}-600">
                                ${performance.status_code || 'N/A'}
                            </p>
                        </div>
                    </div>
                </div>
                ` : ''}

                <!-- Performance Recommendations -->
                <div class="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="zap" class="w-5 h-5 mr-2"></i>
                        Performance Recommendations
                    </h4>
                    <div class="space-y-3">
                        ${this.generatePerformanceRecommendations(aggregateStats, performance)}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('performance_content').innerHTML = html;
    }

    displayRecommendations(results) {
        const recommendations = results.recommendations || [];

        // Handle new categorized format from enhanced analyzer
        let grouped = {};
        let totalRecommendations = 0;

        if (typeof recommendations === 'object' && !Array.isArray(recommendations)) {
            // New categorized format
            if (recommendations.critical && recommendations.critical.length > 0) {
                grouped['critical'] = recommendations.critical;
                totalRecommendations += recommendations.critical.length;
            }
            if (recommendations.high_impact && recommendations.high_impact.length > 0) {
                grouped['high'] = recommendations.high_impact;
                totalRecommendations += recommendations.high_impact.length;
            }
            if (recommendations.medium_impact && recommendations.medium_impact.length > 0) {
                grouped['medium'] = recommendations.medium_impact;
                totalRecommendations += recommendations.medium_impact.length;
            }
            if (recommendations.low_impact && recommendations.low_impact.length > 0) {
                grouped['low'] = recommendations.low_impact;
                totalRecommendations += recommendations.low_impact.length;
            }
        } else {
            // Legacy array format
            grouped = this.groupRecommendations(Array.isArray(recommendations) ? recommendations : []);
            totalRecommendations = Array.isArray(recommendations) ? recommendations.length : 0;
        }

        const html = `
            <div class="space-y-6">
                ${Object.entries(grouped).map(([priority, items]) => `
                    <div class="bg-white p-6 rounded-lg border border-gray-200">
                        <h4 class="text-lg font-semibold mb-4 flex items-center">
                            <i data-lucide="alert-${priority === 'critical' || priority === 'high' ? 'triangle' : priority === 'medium' ? 'circle' : 'info'}" 
                               class="w-5 h-5 mr-2 text-${priority === 'critical' ? 'red' : priority === 'high' ? 'red' : priority === 'medium' ? 'yellow' : 'blue'}-600"></i>
                            ${priority === 'critical' ? 'Critical' : priority.charAt(0).toUpperCase() + priority.slice(1)} Priority Issues (${items.length})
                        </h4>
                        <div class="space-y-4">
                            ${items.map(rec => `
                                <div class="border-l-4 border-${priority === 'critical' || priority === 'high' ? 'red' : priority === 'medium' ? 'yellow' : 'blue'}-500 pl-4">
                                    <h5 class="font-medium text-${priority === 'critical' || priority === 'high' ? 'red' : priority === 'medium' ? 'yellow' : 'blue'}-800">
                                        ${rec.type || rec.title || 'SEO Issue'}
                                    </h5>
                                    <p class="text-gray-700 mb-2">${rec.title || rec.message || rec.issue || 'No description available'}</p>
                                    ${rec.solution || rec.fix ? `
                                        <div class="bg-blue-50 p-3 rounded text-sm">
                                            <strong class="text-blue-800">Solution:</strong> 
                                            <span class="text-blue-700">${rec.solution || rec.fix}</span>
                                        </div>
                                    ` : ''}
                                    ${rec.impact ? `
                                        <div class="mt-2 text-sm text-gray-600">
                                            <strong>Impact:</strong> ${rec.impact}
                                        </div>
                                    ` : ''}
                                    ${rec.estimated_effort ? `
                                        <div class="mt-1 text-sm text-gray-600">
                                            <strong>Effort:</strong> ${rec.estimated_effort}
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
                
                ${totalRecommendations === 0 ? `
                    <div class="bg-green-50 border border-green-200 p-6 rounded-lg text-center">
                        <i data-lucide="check-circle" class="w-12 h-12 text-green-600 mx-auto mb-3"></i>
                        <h4 class="text-lg font-semibold text-green-800 mb-2">Great Job!</h4>
                        <p class="text-green-700">No major SEO issues were found. Your website is well-optimized!</p>
                    </div>
                ` : ''}
            </div>
        `;

        document.getElementById('recommendations_content').innerHTML = html;
    }

    displayPagesAnalyzed(results) {
        const pages = results.pages_analysis?.pages || {};
        const pagesArray = Object.entries(pages);

        const html = `
            <div class="space-y-4">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-semibold mb-2">Pages Analyzed: ${pagesArray.length}</h4>
                    <p class="text-sm text-gray-600">Detailed analysis of each page found during crawling</p>
                </div>
                
                <div class="space-y-4">
                    ${pagesArray.map(([url, pageData]) => `
                        <div class="bg-white p-6 rounded-lg border border-gray-200">
                            <div class="mb-4">
                                <h5 class="font-semibold text-blue-600 break-all">${url}</h5>
                                <div class="flex items-center space-x-4 mt-2 text-sm">
                                    <span class="px-2 py-1 bg-${this.getScoreColor(pageData.page_score)}-100 text-${this.getScoreColor(pageData.page_score)}-800 rounded">
                                        Score: ${pageData.page_score || 0}/100
                                    </span>
                                    <span class="text-gray-600">
                                        Load Time: ${pageData.performance?.load_time || 0}s
                                    </span>
                                    <span class="text-gray-600">
                                        Size: ${Math.round((pageData.performance?.content_size || 0) / 1024)} KB
                                    </span>
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <!-- Title -->
                                <div>
                                    <p class="text-sm font-medium text-gray-700">Title</p>
                                    <p class="text-sm text-gray-600 truncate" title="${pageData.title?.text || 'Missing'}">
                                        ${pageData.title?.text || 'Missing'}
                                    </p>
                                    <p class="text-xs text-gray-500">${pageData.title?.length || 0} chars</p>
                                </div>
                                
                                <!-- Meta Description -->
                                <div>
                                    <p class="text-sm font-medium text-gray-700">Meta Description</p>
                                    <p class="text-sm text-gray-600 truncate" title="${pageData.meta?.description?.text || 'Missing'}">
                                        ${pageData.meta?.description?.text || 'Missing'}
                                    </p>
                                    <p class="text-xs text-gray-500">${pageData.meta?.description?.length || 0} chars</p>
                                </div>
                                
                                <!-- H1 Count -->
                                <div>
                                    <p class="text-sm font-medium text-gray-700">H1 Tags</p>
                                    <p class="text-sm font-bold text-${pageData.headings?.h1_count === 1 ? 'green' : 'red'}-600">
                                        ${pageData.headings?.h1_count || 0}
                                    </p>
                                    <p class="text-xs text-gray-500">
                                        ${pageData.headings?.h1_count === 1 ? 'Perfect' : pageData.headings?.h1_count > 1 ? 'Too many' : 'Missing'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                ${pagesArray.length === 0 ? `
                    <div class="bg-yellow-50 border border-yellow-200 p-6 rounded-lg text-center">
                        <i data-lucide="alert-circle" class="w-8 h-8 text-yellow-600 mx-auto mb-3"></i>
                        <p class="text-yellow-800">No pages were successfully analyzed. This might indicate crawling issues.</p>
                    </div>
                ` : ''}
            </div>
        `;

        document.getElementById('pages_content').innerHTML = html;
    }

    // Helper methods
    countIssues(results) {
        const recommendations = results.recommendations || [];

        // Handle new categorized format
        if (typeof recommendations === 'object' && !Array.isArray(recommendations)) {
            let totalIssues = 0;
            if (recommendations.critical) totalIssues += recommendations.critical.length;
            if (recommendations.high_impact) totalIssues += recommendations.high_impact.length;
            if (recommendations.medium_impact) totalIssues += recommendations.medium_impact.length;
            if (recommendations.low_impact) totalIssues += recommendations.low_impact.length;
            return totalIssues;
        }

        // Handle legacy array format
        return Array.isArray(recommendations) ?
            recommendations.filter(rec => rec.type === 'error' || rec.type === 'warning').length : 0;
    }

    countCriticalIssues(results) {
        const recommendations = results.recommendations || [];

        // Handle new categorized format
        if (typeof recommendations === 'object' && !Array.isArray(recommendations)) {
            return (recommendations.critical ? recommendations.critical.length : 0) +
                (recommendations.high_impact ? recommendations.high_impact.length : 0);
        }

        // Handle legacy array format
        return Array.isArray(recommendations) ?
            recommendations.filter(rec => rec.priority === 'high' || rec.type === 'error').length : 0;
    }

    countWarningIssues(results) {
        const recommendations = results.recommendations || [];

        // Handle new categorized format
        if (typeof recommendations === 'object' && !Array.isArray(recommendations)) {
            return (recommendations.medium_impact ? recommendations.medium_impact.length : 0) +
                (recommendations.low_impact ? recommendations.low_impact.length : 0);
        }

        // Handle legacy array format
        return Array.isArray(recommendations) ?
            recommendations.filter(rec => rec.priority === 'medium' || rec.type === 'warning').length : 0;
    }

    getScoreGrade(score) {
        if (score >= 90) return 'A+';
        if (score >= 80) return 'A';
        if (score >= 70) return 'B';
        if (score >= 60) return 'C';
        if (score >= 50) return 'D';
        return 'F';
    }

    generateScoreBreakdown(results) {
        const technical = results.technical_analysis || {};
        const pages = results.pages_analysis || {};

        const breakdowns = [
            {
                label: 'Technical SEO',
                score: this.calculateTechnicalScore(technical),
                color: 'blue'
            },
            {
                label: 'Content Quality',
                score: this.calculateContentScore(pages),
                color: 'green'
            },
            {
                label: 'Performance',
                score: this.calculatePerformanceScore(results),
                color: 'purple'
            },
            {
                label: 'Accessibility',
                score: this.calculateAccessibilityScore(results),
                color: 'orange'
            }
        ];

        return breakdowns.map(item => `
            <div class="text-center">
                <div class="w-16 h-16 mx-auto mb-2 rounded-full bg-${item.color}-100 flex items-center justify-center">
                    <span class="text-${item.color}-600 font-bold text-lg">${item.score}</span>
                </div>
                <p class="text-sm font-medium text-gray-700">${item.label}</p>
                <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div class="bg-${item.color}-500 h-2 rounded-full transition-all duration-500" style="width: ${item.score}%"></div>
                </div>
            </div>
        `).join('');
    }

    calculateTechnicalScore(technical) {
        // Use the new data structure from enhanced analyzer
        const details = technical.details || {};
        let score = 0;
        let factors = 0;

        // HTTPS coverage
        if (details.https_coverage !== undefined) {
            score += details.https_coverage || 0;
            factors++;
        }
        
        // Canonical coverage
        if (details.canonical_coverage !== undefined) {
            score += details.canonical_coverage || 0;
            factors++;
        }
        
        // Schema coverage
        if (details.schema_coverage !== undefined) {
            score += details.schema_coverage || 0;
            factors++;
        }

        // If we have the score directly from the API, use it
        if (technical.score !== undefined) {
            return technical.score;
        }

        return factors > 0 ? Math.round(score / factors) : 0;
    }

    calculateContentScore(pages) {
        // Use the new data structure from enhanced analyzer
        const details = pages.details || {};
        
        // If we have the score directly from the API, use it
        if (pages.score !== undefined) {
            return pages.score;
        }
        
        let score = 100;

        // Deduct points for missing elements
        if (details.missing_titles > 0) score -= 20;
        if (details.missing_meta_descriptions > 0) score -= 15;

        // Adjust for title and meta lengths
        const avgTitleLen = details.avg_title_length || 0;
        if (avgTitleLen < 30 || avgTitleLen > 60) score -= 10;

        const avgMetaLen = details.avg_meta_description_length || 0;
        if (avgMetaLen < 120 || avgMetaLen > 160) score -= 10;

        // Alt text coverage
        const altCoverage = details.alt_text_coverage || 0;
        if (altCoverage < 90) score -= 15;

        return Math.max(0, score);
    }

    calculatePerformanceScore(results) {
        // Use the new data structure from enhanced analyzer
        const performance = results.site_wide_issues || {};
        const details = performance.details || {};
        
        // If we have the score directly from the API, use it
        if (performance.score !== undefined) {
            return performance.score;
        }
        
        let score = 100;

        const avgPageSize = details.avg_page_size || 0;
        if (avgPageSize > 1000) score -= 20;
        else if (avgPageSize > 500) score -= 10;

        const avgLoadTime = details.avg_load_time || 0;
        if (avgLoadTime > 3) score -= 30;
        else if (avgLoadTime > 2) score -= 20;
        else if (avgLoadTime > 1) score -= 10;

        return Math.max(0, score);
    }

    calculateAccessibilityScore(results) {
        const stats = results.pages_analysis?.aggregate_stats || {};
        let score = 100;

        const totalImages = stats.total_images || 0;
        const missingAlt = stats.images_missing_alt || 0;

        if (totalImages > 0) {
            const altCoverage = ((totalImages - missingAlt) / totalImages) * 100;
            score = Math.round(altCoverage);
        }

        return Math.max(0, score);
    }

    calculateAltCoverage(stats) {
        const total = stats.total_images || 0;
        const missing = stats.images_missing_alt || 0;
        if (total === 0) return 100;
        return Math.round(((total - missing) / total) * 100);
    }

    getTitleStatus(title) {
        if (!title || !title.text) return 'red-500';
        const length = title.length || 0;
        if (length >= 30 && length <= 60) return 'green-500';
        if (length >= 20 && length <= 70) return 'yellow-500';
        return 'red-500';
    }

    getMetaStatus(meta) {
        if (!meta || !meta.text) return 'red-500';
        const length = meta.length || 0;
        if (length >= 120 && length <= 160) return 'green-500';
        if (length >= 100 && length <= 180) return 'yellow-500';
        return 'red-500';
    }

    getPerformanceColor(score) {
        if (score >= 80) return 'green';
        if (score >= 60) return 'yellow';
        return 'red';
    }

    getScoreColor(score) {
        if (score >= 80) return 'green';
        if (score >= 60) return 'yellow';
        return 'red';
    }

    generatePerformanceRecommendations(aggregateStats, performance) {
        const recommendations = [];

        if ((aggregateStats.avg_page_size || 0) > 1000) {
            recommendations.push('Consider optimizing images and compressing assets to reduce page size');
        }

        if ((performance.load_time || 0) > 3) {
            recommendations.push('Page load time is slow. Consider optimizing server response time');
        }

        if ((performance.content_size || 0) > 500000) {
            recommendations.push('Large content size detected. Consider code minification and compression');
        }

        if (recommendations.length === 0) {
            recommendations.push('Performance looks good! Keep monitoring for continued optimization');
        }

        return recommendations.map(rec => `
            <div class="flex items-start">
                <i data-lucide="lightbulb" class="w-4 h-4 text-blue-500 mr-2 mt-1 flex-shrink-0"></i>
                <span class="text-gray-700">${rec}</span>
            </div>
        `).join('');
    }

    groupRecommendations(recommendations) {
        // Handle array format only (legacy support)
        if (!Array.isArray(recommendations)) {
            return {};
        }

        return recommendations.reduce((acc, rec) => {
            const priority = rec.priority || 'low';
            if (!acc[priority]) acc[priority] = [];
            acc[priority].push(rec);
            return acc;
        }, {});
    }
}

// Initialize the SEO Audit Display when the page loads
document.addEventListener('DOMContentLoaded', function () {
    new SEOAuditDisplay();

    // Initialize Lucide icons after content is loaded
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

// Tab switching functionality
function switchTab(tabName) {
    // Hide all tab contents
    const contents = document.querySelectorAll('[id$="_content"]');
    contents.forEach(content => content.classList.add('hidden'));

    // Remove active class from all tabs
    const tabs = document.querySelectorAll('[onclick^="switchTab"]');
    tabs.forEach(tab => {
        tab.classList.remove('border-blue-500', 'text-blue-600');
        tab.classList.add('border-transparent', 'text-gray-500');
    });

    // Show selected tab content
    document.getElementById(tabName + '_content').classList.remove('hidden');

    // Add active class to selected tab
    event.target.classList.remove('border-transparent', 'text-gray-500');
    event.target.classList.add('border-blue-500', 'text-blue-600');

    // Reinitialize Lucide icons for new content
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}
