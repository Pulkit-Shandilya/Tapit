"""
Merchant Management API Routes
Handles merchant creation, retrieval, and management
"""

from flask import Blueprint, request, jsonify
import uuid
import secrets

merchants_bp = Blueprint('merchants', __name__)

# In-memory merchant storage (replace with database in production)
merchants_storage = {}


@merchants_bp.route('/create', methods=['POST'])
def create_merchant():
    """
    Create a new merchant with blockchain wallet
    
    Request body:
    {
        "merchant_id": "MERCHANT001" (optional - auto-generated if not provided)
    }
    
    Response:
    {
        "success": true,
        "merchant": {
            "merchant_id": "MERCHANT001",
            "blockchain_wallet": "0x...",
            "created_at": "..."
        }
    }
    """
    try:
        data = request.get_json() or {}
        merchant_id = data.get('merchant_id', f'MERCHANT{uuid.uuid4().hex[:8].upper()}')
        
        # Check if merchant already exists
        if merchant_id in merchants_storage:
            return jsonify({
                'success': False,
                'error': f'Merchant {merchant_id} already exists'
            }), 409
        
        # Create new merchant
        merchant = {
            'merchant_id': merchant_id,
            'blockchain_wallet': f'0x{secrets.token_hex(20)}',
            'created_at': str(__import__('datetime').datetime.now().isoformat())
        }
        
        merchants_storage[merchant_id] = merchant
        
        return jsonify({
            'success': True,
            'message': f'Merchant {merchant_id} created successfully',
            'merchant': merchant
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@merchants_bp.route('/<merchant_id>', methods=['GET'])
def get_merchant(merchant_id):
    """
    Get merchant details by merchant_id
    
    Response:
    {
        "merchant_id": "MERCHANT001",
        "blockchain_wallet": "0x...",
        "created_at": "..."
    }
    """
    try:
        merchant = merchants_storage.get(merchant_id)
        
        if not merchant:
            return jsonify({'error': f'Merchant {merchant_id} not found'}), 404
        
        return jsonify(merchant), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@merchants_bp.route('/', methods=['GET'])
def list_merchants():
    """
    List all merchants
    
    Response:
    {
        "total_merchants": 3,
        "merchants": [...]
    }
    """
    try:
        return jsonify({
            'total_merchants': len(merchants_storage),
            'merchants': list(merchants_storage.values())
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@merchants_bp.route('/<merchant_id>', methods=['DELETE'])
def delete_merchant(merchant_id):
    """Delete a merchant by merchant_id"""
    try:
        if merchant_id not in merchants_storage:
            return jsonify({'error': f'Merchant {merchant_id} not found'}), 404
        
        deleted_merchant = merchants_storage.pop(merchant_id)
        
        return jsonify({
            'success': True,
            'message': f'Merchant {merchant_id} deleted successfully',
            'merchant': deleted_merchant
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@merchants_bp.route('/<merchant_id>', methods=['PUT'])
def update_merchant(merchant_id):
    """Update merchant information"""
    try:
        if merchant_id not in merchants_storage:
            return jsonify({'error': f'Merchant {merchant_id} not found'}), 404
        
        data = request.get_json() or {}
        merchant = merchants_storage[merchant_id]
        
        # Update allowed fields
        if 'blockchain_wallet' in data:
            merchant['blockchain_wallet'] = data['blockchain_wallet']
        
        merchant['updated_at'] = str(__import__('datetime').datetime.now().isoformat())
        
        return jsonify({
            'success': True,
            'message': f'Merchant {merchant_id} updated successfully',
            'merchant': merchant
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Export merchants storage for use in other modules
__all__ = ['merchants_bp', 'merchants_storage']
