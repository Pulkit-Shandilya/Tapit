"""
Payment Processing API Routes
Handles payment transaction processing through the payment flow
"""

from flask import Blueprint, request, jsonify
from app.routes.users_routes import users_storage
from app.routes.merchants_routes import merchants_storage
import uuid
import hashlib
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

# In-memory payment storage
payments_storage = []

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
        return True, f"Transaction approved (amount: {amount})"
    else:
        return False, f"Transaction declined - Amount exceeds limit ({amount} > {SMART_CONTRACT_CONFIG['max_amount']})"


def compute_hash(data):
    """Compute SHA256 hash of transaction data"""
    data_str = str(data)
    return hashlib.sha256(data_str.encode()).hexdigest()


@payments_bp.route('/process', methods=['POST'])
def process_payment():
    """
    Process a payment transaction through the complete payment flow
    
    Request body:
    {
        "user_id": "USER001",
        "merchant_id": "MERCHANT001",
        "amount": 5000
    }
    
    Response:
    {
        "success": true,
        "transaction": {
            "transaction_id": "...",
            "status": "completed",
            "amount": 5000,
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'merchant_id', 'amount']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        user_id = data['user_id']
        merchant_id = data['merchant_id']
        amount = data['amount']
        
        # Validate user and merchant exist
        if user_id not in users_storage:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        if merchant_id not in merchants_storage:
            return jsonify({'error': f'Merchant {merchant_id} not found'}), 404
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # Step 1: SIM Processing
        transaction = {
            'user_id': user_id,
            'merchant_id': merchant_id,
            'card_details': users_storage[user_id]['card_details'],
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'transaction_id': str(uuid.uuid4()),
            'status': None,
            'flow_type': 'payment'
        }
        
        print(f"[SIM] Initiating payment - {transaction['transaction_id']}")
        
        # Step 2: NFC Chip Processing
        print(f"[NFC Chip] Transmitting transaction to POS")
        
        # Step 3: Merchant POS Processing
        print(f"[POS] Received and processing - {transaction['transaction_id']}")
        
        # Step 4: Smart Contract Validation
        is_valid, msg = validate_smart_contract(transaction)
        print(f"[Smart Contract] {msg}")
        
        if not is_valid:
            transaction['status'] = 'declined'
            payments_storage.append(transaction)
            return jsonify({
                'success': False,
                'transaction': transaction
            }), 200
        
        # Step 5: Acquiring Bank Processing
        transaction['acquiring_bank_status'] = 'processed'
        transaction['acquiring_block_hash'] = compute_hash(transaction)
        print(f"[Acquiring Bank] Processing - Hash: {transaction['acquiring_block_hash'][:16]}...")
        
        # Step 6: Card Scheme Processing
        transaction['card_scheme_status'] = 'routed'
        print(f"[Card Scheme] Routing to Issuing Bank")
        
        # Step 7: Issuing Bank Processing
        transaction['issuing_bank_status'] = 'authorized'
        transaction['issuing_block_hash'] = compute_hash(transaction)
        print(f"[Issuing Bank] Validating - Hash: {transaction['issuing_block_hash'][:16]}...")
        
        # Step 8: Finalize
        transaction['status'] = 'completed'
        payments_storage.append(transaction)
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'transaction': transaction
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction details by transaction_id"""
    try:
        for transaction in payments_storage:
            if transaction['transaction_id'] == transaction_id:
                return jsonify(transaction), 200
        
        return jsonify({'error': f'Transaction {transaction_id} not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/', methods=['GET'])
def list_payments():
    """
    List all payment transactions
    
    Query parameters:
    - user_id: Filter by user
    - merchant_id: Filter by merchant
    - status: Filter by status (completed, declined)
    """
    try:
        query_user = request.args.get('user_id')
        query_merchant = request.args.get('merchant_id')
        query_status = request.args.get('status')
        
        filtered_payments = payments_storage
        
        if query_user:
            filtered_payments = [p for p in filtered_payments if p['user_id'] == query_user]
        
        if query_merchant:
            filtered_payments = [p for p in filtered_payments if p['merchant_id'] == query_merchant]
        
        if query_status:
            filtered_payments = [p for p in filtered_payments if p['status'] == query_status]
        
        return jsonify({
            'total_transactions': len(filtered_payments),
            'transactions': filtered_payments
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/smart-contract', methods=['GET'])
def get_smart_contract():
    """Get smart contract configuration"""
    try:
        return jsonify({
            'max_amount': SMART_CONTRACT_CONFIG['max_amount'],
            'valid_until': SMART_CONTRACT_CONFIG['valid_until'],
            'description': 'Smart contract enforces transaction limits'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Export for use in other modules
__all__ = ['payments_bp', 'payments_storage', 'SMART_CONTRACT_CONFIG']
