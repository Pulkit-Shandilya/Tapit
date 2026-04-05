"""
Authorization Processing API Routes
Handles authorization transactions through the authorization flow
"""

from flask import Blueprint, request, jsonify
from app.routes.users_routes import users_storage
import uuid
import hashlib
from datetime import datetime

authorization_bp = Blueprint('authorization', __name__)

# In-memory authorization storage
authorization_storage = []

# Smart Contract Configuration
SMART_CONTRACT_CONFIG = {
    'max_amount': 10000,
    'valid_until': '2025-12-31'
}


def validate_smart_contract(transaction_data):
    """
    Smart Contract Validation
    Returns: (bool, str) - (is_valid, message)
    """
    amount = transaction_data.get('amount', 0)
    
    if amount <= SMART_CONTRACT_CONFIG['max_amount']:
        return True, f"Authorization approved (amount: {amount})"
    else:
        return False, f"Authorization declined - Amount exceeds limit ({amount} > {SMART_CONTRACT_CONFIG['max_amount']})"


def compute_hash(data):
    """Compute SHA256 hash of transaction data"""
    data_str = str(data)
    return hashlib.sha256(data_str.encode()).hexdigest()


@authorization_bp.route('/authorize', methods=['POST'])
def authorize_transaction():
    """
    Process an authorization transaction through the authorization flow
    
    Request body:
    {
        "user_id": "USER001",
        "amount": 5000
    }
    
    Response:
    {
        "success": true,
        "transaction": {
            "transaction_id": "...",
            "status": "authorized",
            "amount": 5000,
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'amount']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        user_id = data['user_id']
        amount = data['amount']
        
        # Validate user exists
        if user_id not in users_storage:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # Step 1: SIM Processing
        transaction = {
            'user_id': user_id,
            'card_details': users_storage[user_id]['card_details'],
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'transaction_id': str(uuid.uuid4()),
            'status': None,
            'flow_type': 'authorization'
        }
        
        print(f"[SIM] Initiating authorization - {transaction['transaction_id']}")
        
        # Step 2: BaseBand Processing
        transaction['emulation_status'] = 'emulated'
        print(f"[BaseBand] Emulating POS - {transaction['transaction_id']}")
        
        # Step 3: OTA Platform Processing
        transaction['ota_status'] = 'processed'
        print(f"[OTA Platform] Processing authorization")
        
        # Step 4: Smart Contract Validation
        is_valid, msg = validate_smart_contract(transaction)
        print(f"[Smart Contract] {msg}")
        
        if not is_valid:
            transaction['status'] = 'declined'
            authorization_storage.append(transaction)
            return jsonify({
                'success': False,
                'transaction': transaction
            }), 200
        
        # Step 5: Issuing Bank Processing
        transaction['issuing_bank_status'] = 'authorized'
        transaction['issuing_block_hash'] = compute_hash(transaction)
        print(f"[Issuing Bank] Validating - Hash: {transaction['issuing_block_hash'][:16]}...")
        
        # Step 6: Finalize
        transaction['status'] = 'authorized'
        authorization_storage.append(transaction)
        
        return jsonify({
            'success': True,
            'message': 'Authorization processed successfully',
            'transaction': transaction
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authorization_bp.route('/<transaction_id>', methods=['GET'])
def get_authorization(transaction_id):
    """Get authorization transaction details by transaction_id"""
    try:
        for transaction in authorization_storage:
            if transaction['transaction_id'] == transaction_id:
                return jsonify(transaction), 200
        
        return jsonify({'error': f'Authorization {transaction_id} not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authorization_bp.route('/', methods=['GET'])
def list_authorizations():
    """
    List all authorization transactions
    
    Query parameters:
    - user_id: Filter by user
    - status: Filter by status (authorized, declined)
    """
    try:
        query_user = request.args.get('user_id')
        query_status = request.args.get('status')
        
        filtered_authorizations = authorization_storage
        
        if query_user:
            filtered_authorizations = [a for a in filtered_authorizations if a['user_id'] == query_user]
        
        if query_status:
            filtered_authorizations = [a for a in filtered_authorizations if a['status'] == query_status]
        
        return jsonify({
            'total_authorizations': len(filtered_authorizations),
            'authorizations': filtered_authorizations
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authorization_bp.route('/smart-contract', methods=['GET'])
def get_smart_contract():
    """Get smart contract configuration"""
    try:
        return jsonify({
            'max_amount': SMART_CONTRACT_CONFIG['max_amount'],
            'valid_until': SMART_CONTRACT_CONFIG['valid_until'],
            'description': 'Smart contract enforces authorization limits'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Export for use in other modules
__all__ = ['authorization_bp', 'authorization_storage', 'SMART_CONTRACT_CONFIG']
