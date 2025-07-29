"""
Application entry point using improved structure.
This file serves as the main entry point for the Flask application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.factory import create_app

# Create application instance
app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    # Development server configuration
    port = int(os.environ.get("PORT", 5002))  # Use port 5002 to avoid conflicts
    debug = os.environ.get("FLASK_ENV") == "development"

    app.run(host="0.0.0.0", port=port, debug=True)  # Force debug mode to see errors
