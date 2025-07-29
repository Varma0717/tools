"""
Meta Tag Analyzer utility functions.
"""

import requests
import re
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional
from datetime import datetime


class MetaTagAnalyzer:
    """Main utility class for meta tag analyzer functionality."""
    
    def __init__(self):
        self.timeout = 10
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data and return cleaned data."""
        try:
            cleaned_data = {}
            
            # Common validation patterns
            if 'url' in data:
                url = data.get('url', '').strip()
                if not url:
                    return {"success": False, "error": "URL is required"}
                
                # Add protocol if missing
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                # Validate URL format
                try:
                    parsed = urlparse(url)
                    if not parsed.netloc:
                        return {"success": False, "error": "Invalid URL format"}
                    cleaned_data['url'] = url
                except Exception:
                    return {"success": False, "error": "Invalid URL format"}
            
            if 'text' in data:
                text = data.get('text', '').strip()
                if not text:
                    return {"success": False, "error": "Text content is required"}
                cleaned_data['text'] = text
            
            return {"success": True, "data": cleaned_data}
            
        except Exception as e:
            return {"success": False, "error": f"Validation error: {str(e)}"}
    
    def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing function for meta tag analyzer."""
        try:
            # Validate input first
            validation = self.validate_input(data)
            if not validation["success"]:
                return validation
            
            cleaned_data = validation["data"]
            
            # Implement specific meta tag analyzer logic here
            result = self.analyze(cleaned_data)
            
            return {
                "success": True,
                "results": result,
                "timestamp": str(datetime.now()),
                "tool": "meta_tag_analyzer"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Meta Tag Analyzer analysis failed: {str(e)}"
            }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the main analysis for meta tag analyzer."""
        try:
            # TODO: Implement specific analysis logic
            analysis_results = {
                "status": "analyzed",
                "data": data,
                "message": f"Meta Tag Analyzer analysis completed"
            }
            
            return analysis_results
            
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")
    
    def make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make HTTP request with proper error handling."""
        try:
            default_headers = {"User-Agent": self.user_agent}
            if headers:
                default_headers.update(headers)
            
            response = requests.get(
                url, 
                headers=default_headers, 
                timeout=self.timeout,
                allow_redirects=True
            )
            return response
            
        except Exception as e:
            print(f"Request failed: {str(e)}")
            return None
    
    def format_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        try:
            return {
                "success": True,
                "formatted_data": data,
                "summary": f"Meta Tag Analyzer analysis completed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Formatting failed: {str(e)}"
            }
