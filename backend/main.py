"""
Tapit - NFC Payment System
Main entry point for the Flask application
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
except ImportError as e:
    print(f"Error importing app module: {e}")
    print("Make sure you have all dependencies installed: pip install -r requirements.txt")
    sys.exit(1)

# Create Flask app instance
try:
    app = create_app(os.getenv('FLASK_ENV', 'development'))
except Exception as e:
    print(f"Error creating Flask app: {e}")
    sys.exit(1)


@app.shell_context_processor
def make_shell_context():
    """Make db available in Flask shell"""
    return {'db': db}


@app.before_request
def before_request():
    """Initialize database tables if they don't exist"""
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting Tapit API Server")
    print(f"{'='*60}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug Mode: {debug}")
    print(f"Database: {os.getenv('DATABASE_URL', 'sqlite:///tapit.db')}")
    print(f"{'='*60}\n")
    print(f"👉 API will be available at: http://{host}:{port}")
    print(f"👉 Health Check: http://{host}:{port}/api/health\n")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"Error running Flask app: {e}")
        sys.exit(1)
