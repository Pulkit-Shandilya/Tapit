"""
Payment Processing API Routes
Handles payment transaction processing through the payment flow
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.payment import Payment
from app.routes.users_routes import users_storage
from app.routes.merchants_routes import merchants_storage
import uuid
import hashlib
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

# In-memory payment storage
payments_storage = []


def _ensure_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        return user
    return None

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


@payments_bp.route('/transfer', methods=['POST'])
def transfer_wallet_balance():
    """Transfer wallet balance between two database-backed users."""
    try:
        data = request.get_json() or {}
        sender_id = data.get('from_user_id')
        receiver_id = data.get('to_user_id')
        amount = float(data.get('amount', 0))

        if not sender_id or not receiver_id:
            return jsonify({'error': 'from_user_id and to_user_id are required'}), 400

        if sender_id == receiver_id:
            return jsonify({'error': 'Sender and receiver must be different users'}), 400

        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400

        sender = _ensure_user(sender_id)
        receiver = _ensure_user(receiver_id)

        if sender is None:
            return jsonify({'error': f'Sender {sender_id} not found'}), 404

        if receiver is None:
            return jsonify({'error': f'Receiver {receiver_id} not found'}), 404

        if sender.wallet_balance < amount:
            return jsonify({'error': 'Insufficient balance'}), 400

        sender.wallet_balance -= amount
        receiver.wallet_balance += amount

        transaction = {
            'transaction_id': str(uuid.uuid4()),
            'from_user_id': sender_id,
            'to_user_id': receiver_id,
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'flow_type': 'peer_transfer',
        }

        transaction['block_hash'] = compute_hash(transaction)
        payments_storage.append(transaction)

        payment_record = Payment(
            transaction_id=transaction['transaction_id'],
            from_user_id=sender_id,
            to_user_id=receiver_id,
            amount=amount,
            status='completed',
            flow_type='peer_transfer',
            block_hash=transaction['block_hash'],
        )
        db.session.add(payment_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Transfer completed successfully',
            'transaction': transaction,
            'sender_balance': sender.wallet_balance,
            'receiver_balance': receiver.wallet_balance,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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

        payment_record = Payment(
            transaction_id=transaction['transaction_id'],
            user_id=user_id,
            merchant_id=merchant_id,
            amount=amount,
            status='completed',
            flow_type='payment',
            block_hash=transaction['issuing_block_hash'],
            acquiring_bank_status=transaction['acquiring_bank_status'],
            issuing_bank_status=transaction['issuing_bank_status'],
            note='Merchant payment',
        )
        db.session.add(payment_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'transaction': transaction
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/history', methods=['GET'])
def get_payment_history():
    """Return persisted payment history from the database."""
    try:
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        flow_type = request.args.get('flow_type')

        query = Payment.query.order_by(Payment.created_at.desc())

        if user_id:
            query = query.filter(
                (Payment.user_id == user_id)
                | (Payment.from_user_id == user_id)
                | (Payment.to_user_id == user_id)
            )

        if status:
            query = query.filter_by(status=status)

        if flow_type:
            query = query.filter_by(flow_type=flow_type)

        payments = query.all()

        return jsonify({
            'success': True,
            'total_transactions': len(payments),
            'transactions': [payment.to_dict() for payment in payments],
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
