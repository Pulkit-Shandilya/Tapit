"""
User Model
Represents a user in the NFC payment system with blockchain wallet integration
"""

from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy (should be imported from app/__init__.py in production)
db = SQLAlchemy()


class User(db.Model):
    """
    User model for the NFC payment system
    Stores user information, authentication, and blockchain wallet details
    """
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic Information
    user_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile Information
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone_number = db.Column(db.String(20))
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # Blockchain & Wallet
    blockchain_wallet = db.Column(db.String(255), unique=True, index=True)
    wallet_balance = db.Column(db.Float, default=0.0)
    
    # NFC Card Details
    nfc_card_id = db.Column(db.String(100), unique=True, index=True)
    nfc_card_linked = db.Column(db.Boolean, default=False)
    
    # Account Status

    is_verified = db.Column(db.Boolean, default=False)
    is_merchant = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    # Relationships (for future implementation)
    # transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    # payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the user's password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """
        Convert user object to dictionary
        
        Args:
            include_sensitive (bool): Whether to include sensitive data like password hash
        
        Returns:
            dict: User data as dictionary
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'blockchain_wallet': self.blockchain_wallet,
            'wallet_balance': self.wallet_balance,
            'nfc_card_id': self.nfc_card_id,
            'nfc_card_linked': self.nfc_card_linked,
            'is_verified': self.is_verified,
            'is_merchant': self.is_merchant,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def to_json(self, include_sensitive=False):
        """Convert user object to JSON"""
        return jsonify(self.to_dict(include_sensitive=include_sensitive))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @classmethod
    def find_by_user_id(cls, user_id):
        """Find user by user_id"""
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def find_by_username(cls, username):
        """Find user by username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_wallet(cls, wallet_address):
        """Find user by blockchain wallet address"""
        return cls.query.filter_by(blockchain_wallet=wallet_address).first()
    
    @classmethod
    def find_by_nfc_card(cls, card_id):
        """Find user by NFC card ID"""
        return cls.query.filter_by(nfc_card_id=card_id).first()



