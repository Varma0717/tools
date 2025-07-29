"""
Production-ready Flask application entry point.
This is the main file to run your application.
"""

import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Set OAuth2 insecure transport for development
if os.getenv("FLASK_ENV") == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from app.factory import create_app

# Create application instance
app = create_app()

if __name__ == "__main__":
    # Development server
    app.run(host="127.0.0.1", port=5000, debug=os.getenv("FLASK_ENV") == "development")
