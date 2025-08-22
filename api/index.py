# Vercel serverless function entry point
import sys
import os

# Add the parent directory to the Python path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export the Flask app for Vercel
application = app

# This is the handler that Vercel will call
if __name__ == "__main__":
    app.run()