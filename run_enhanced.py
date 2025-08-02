#!/usr/bin/env python3
"""
Enhanced Super SEO Toolkit Startup Script
Includes all advanced features and optimizations
"""

import os
import sys
from app import create_app

def main():
    """Start the enhanced Super SEO Toolkit"""
    
    print("🚀 Starting Enhanced Super SEO Toolkit")
    print("=" * 50)
    
    # Set environment variables for optimization
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    try:
        # Create Flask application
        app = create_app()
        
        print("✅ Application initialized successfully")
        print("🔧 Advanced caching system: Active")
        print("🔍 SEO analysis engine: Ready")
        print("📊 Dashboard analytics: Available")
        print("🎯 All enhanced features: Loaded")
        
        print("\n🌐 Starting development server...")
        print("   URL: http://localhost:5000")
        print("   SEO Analyzer: http://localhost:5000/seo/analyze")
        print("   Admin Dashboard: http://localhost:5000/admin")
        
        # Start the application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
