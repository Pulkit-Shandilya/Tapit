"""
User Management API Routes
Handles user creation, retrieval, and management
"""

from flask import Blueprint, request, jsonify
import uuid
import secrets

users_bp = Blueprint('users', __name__)

# In-memory user storage (replace with database in production)
users_storage = {}


@users_bp.route('/create', methods=['POST'])
def create_user():
    """
    Create a new user with blockchain wallet
    
    Request body:
    {
        "user_id": "USER001" (optional - auto-generated if not provided)
    }
    
    Response:
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
