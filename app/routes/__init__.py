"""
Routes package for NFC Payment System API
Organizes all API endpoints by resource
"""

from flask import Blueprint

# Import route blueprints
from app.routes.users_routes import users_bp
from app.routes.merchants_routes import merchants_bp
from app.routes.payments_routes import payments_bp
from app.routes.authorization_routes import authorization_bp
from app.routes.ledgers_routes import ledgers_bp


def register_routes(app):
    """Register all route blueprints with the Flask app"""
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(merchants_bp, url_prefix='/api/merchants')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(authorization_bp, url_prefix='/api/authorization')
    app.register_blueprint(ledgers_bp, url_prefix='/api/ledgers')


__all__ = [
    'register_routes',
    'users_bp',
    'merchants_bp',
    'payments_bp',
    'authorization_bp',
    'ledgers_bp'
]
