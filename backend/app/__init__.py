"""
Flask App Factory
Initializes and configures the Flask application
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

# Load environment variables
load_dotenv()


def create_app(config_name='development'):
    """
    Application factory function
    Creates and configures the Flask app
    
    Args:
        config_name (str): The configuration environment
    
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///tapit.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JSON_SORT_KEYS'] = False
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import (
        users_routes,
        authorization_routes,
        merchants_routes,
        payments_routes,
        ledgers_routes
    )
    
    app.register_blueprint(users_routes.users_bp, url_prefix='/api/users')
    app.register_blueprint(authorization_routes.authorization_bp, url_prefix='/api/authorization')
    app.register_blueprint(merchants_routes.merchants_bp, url_prefix='/api/merchants')
    app.register_blueprint(payments_routes.payments_bp, url_prefix='/api/payments')
    app.register_blueprint(ledgers_routes.ledgers_bp, url_prefix='/api/ledgers')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'Tapit API is running'}, 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app
