"""
User Management API Routes
Handles user creation, retrieval, and management
"""

from flask import Blueprint, request, jsonify
import uuid
import secrets

from app import db
from app.models.user import User

users_bp = Blueprint('users', __name__)

PRIMARY_USER_ID = 'user_primary'
SECONDARY_USER_ID = 'user_secondary'

# In-memory user storage (replace with database in production)
users_storage = {}


def _seed_default_user(user_id=PRIMARY_USER_ID):
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        return user

    if user_id == PRIMARY_USER_ID:
        first_name = 'Rishabh'
        last_name = 'Parashar'
        email = 'rishabh@tapit.com'
        balance = 245850.00
        phone_number = '+91 98765 43210'
        username = 'rishabh'
    else:
        first_name = 'Priya'
        last_name = 'Sharma'
        email = 'priya@tapit.com'
        balance = 5000.00
        phone_number = '+91 90000 00000'
        username = 'priya'

    user = User(
        user_id=user_id,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        age=24,
        phone_number=phone_number,
        blockchain_wallet=f'0x{secrets.token_hex(20)}',
        wallet_balance=balance,
        nfc_card_id='tapit-demo-card',
        nfc_card_linked=True,
        is_verified=True,
    )
    user.set_password('tapit-demo-password')
    db.session.add(user)
    db.session.commit()
    return user


def _get_profile_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user is None and user_id in {PRIMARY_USER_ID, SECONDARY_USER_ID}:
        user = _seed_default_user(user_id)
    return user


@users_bp.route('/create', methods=['POST'])
def create_user():
    """
    Create a new user with blockchain wallet
    
    Request body:
    {
        "user_id": "USER001" (optional - auto-generated if not provided)
    }
    
    Response:l
    {
        "success": true,
        "user": {
            "user_id": "USER001",
            "blockchain_wallet": "0x...",
            "card_details": {...}
        }
    }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', f'USER{uuid.uuid4().hex[:8].upper()}')
        
        # Check if user already exists
        if user_id in users_storage:
            return jsonify({
                'success': False,
                'error': f'User {user_id} already exists'
            }), 409
        
        # Create new user
        user = {
            'user_id': user_id,
            'blockchain_wallet': f'0x{secrets.token_hex(20)}',
            'card_details': {
                'card_number': secrets.token_hex(8),
                'expiry': '12/25'
            },
            'created_at': str(__import__('datetime').datetime.now().isoformat())
        }
        
        users_storage[user_id] = user
        
        return jsonify({
            'success': True,
            'message': f'User {user_id} created successfully',
            'user': user
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        user = _get_profile_user(user_id)
        if not user:
            return jsonify({'error': f'User {user_id} not found'}), 404

        return jsonify({
            'success': True,
            'profile': user.to_dict(),
            'balance': user.wallet_balance,
            'balance_locked': True,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    try:
        user = _get_profile_user(user_id)
        if not user:
            return jsonify({'error': f'User {user_id} not found'}), 404

        data = request.get_json() or {}

        for field in ['first_name', 'last_name', 'age', 'phone_number', 'email']:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': user.to_dict(),
            'balance': user.wallet_balance,
            'balance_locked': True,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/profile/<user_id>/balance', methods=['GET'])
def get_balance(user_id):
    try:
        user = _get_profile_user(user_id)
        if not user:
            return jsonify({'error': f'User {user_id} not found'}), 404

        return jsonify({
            'success': True,
            'user_id': user.user_id,
            'balance': user.wallet_balance,
            'currency': 'INR',
            'locked': True,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user details by user_id
    
    Response:
    {
        "user_id": "USER001",
        "blockchain_wallet": "0x...",
        "card_details": {...}
    }
    """
    try:
        user = users_storage.get(user_id)
        
        if not user:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        return jsonify(user), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/', methods=['GET'])
def list_users():
    """
    List all users
    
    Response:
    {
        "total_users": 5,
        "users": [...]
    }
    """
    try:
        return jsonify({
            'total_users': len(users_storage),
            'users': list(users_storage.values())
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user by user_id"""
    try:
        if user_id not in users_storage:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        deleted_user = users_storage.pop(user_id)
        
        return jsonify({
            'success': True,
            'message': f'User {user_id} deleted successfully',
            'user': deleted_user
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    try:
        if user_id not in users_storage:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        data = request.get_json() or {}
        user = users_storage[user_id]
        
        # Update allowed fields
        if 'card_details' in data:
            user['card_details'].update(data['card_details'])
        
        user['updated_at'] = str(__import__('datetime').datetime.now().isoformat())
        
        return jsonify({
            'success': True,
            'message': f'User {user_id} updated successfully',
            'user': user
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Export users storage for use in other modules
__all__ = ['users_bp', 'users_storage']
