"""
WSGI entry point for PythonAnywhere deployment.
PythonAnywhere requires a WSGI application to run FastAPI.
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(project_dir / ".env")

# Import the FastAPI app
from main import app

# Create WSGI application
# PythonAnywhere will call this 'application' object
application = app
