import sys
import os

project_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(project_dir, ".env")

# --- Add project directory to sys.path ---
sys.path.insert(0, project_dir)

# --- Import Flask application ---
from app import app as application
