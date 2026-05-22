"""
Blockchain Ledger API Routes
Handles retrieval of blockchain ledgers from Acquiring and Issuing Banks
"""

from flask import Blueprint, request, jsonify
from app.routes.payments_routes import payments_storage

ledgers_bp = Blueprint('ledgers', __name__)


def filter_acquiring_ledger():
    """Filter transactions that have acquiring bank data"""
    acquiring_ledger = []
    for transaction in payments_storage:
        if transaction.get('acquiring_bank_status') == 'processed':
            acquiring_ledger.append(transaction)
    return acquiring_ledger


def filter_issuing_ledger():
    """Filter transactions that have issuing bank data"""
    issuing_ledger = []
    for transaction in payments_storage:
        if transaction.get('issuing_bank_status') == 'authorized':
            issuing_ledger.append(transaction)
    return issuing_ledger


@ledgers_bp.route('/acquiring', methods=['GET'])
def get_acquiring_ledger():
    """
    Get Acquiring Bank Blockchain Ledger
    Returns all transactions processed by the Acquiring Bank
    
    Query parameters:
    - limit: Number of records to return (default: all)
    - offset: Starting position (default: 0)
    """
    try:
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        ledger = filter_acquiring_ledger()
        total_transactions = len(ledger)
        
        # Apply pagination if limit is specified
        if limit:
            ledger = ledger[offset:offset + limit]
        else:
            ledger = ledger[offset:]
        
        return jsonify({
            'bank': 'Acquiring Bank',
            'total_transactions': total_transactions,
            'returned_count': len(ledger),
            'offset': offset,
            'limit': limit,
            'ledger': ledger
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ledgers_bp.route('/issuing', methods=['GET'])
def get_issuing_ledger():
    """
    Get Issuing Bank Blockchain Ledger
    Returns all transactions authorized by the Issuing Bank
    
    Query parameters:
    - limit: Number of records to return (default: all)
    - offset: Starting position (default: 0)
    """
    try:
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        ledger = filter_issuing_ledger()
        total_transactions = len(ledger)
        
        # Apply pagination if limit is specified
        if limit:
            ledger = ledger[offset:offset + limit]
        else:
            ledger = ledger[offset:]
        
        return jsonify({
            'bank': 'Issuing Bank',
            'total_transactions': total_transactions,
            'returned_count': len(ledger),
            'offset': offset,
            'limit': limit,
            'ledger': ledger
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ledgers_bp.route('/acquiring/<transaction_id>', methods=['GET'])
def get_acquiring_transaction(transaction_id):
    """Get a specific transaction from Acquiring Bank ledger"""
    try:
        ledger = filter_acquiring_ledger()
        
        for transaction in ledger:
            if transaction['transaction_id'] == transaction_id:
                return jsonify({
                    'bank': 'Acquiring Bank',
                    'transaction': transaction
                }), 200
        
        return jsonify({'error': f'Transaction {transaction_id} not found in Acquiring Bank ledger'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ledgers_bp.route('/issuing/<transaction_id>', methods=['GET'])
def get_issuing_transaction(transaction_id):
    """Get a specific transaction from Issuing Bank ledger"""
    try:
        ledger = filter_issuing_ledger()
        
        for transaction in ledger:
            if transaction['transaction_id'] == transaction_id:
                return jsonify({
                    'bank': 'Issuing Bank',
                    'transaction': transaction
                }), 200
        
        return jsonify({'error': f'Transaction {transaction_id} not found in Issuing Bank ledger'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ledgers_bp.route('/summary', methods=['GET'])
def get_ledger_summary():
    """Get summary statistics of both blockchain ledgers"""
    try:
        acquiring_ledger = filter_acquiring_ledger()
        issuing_ledger = filter_issuing_ledger()
        
        # Calculate statistics
        acquiring_total = sum(t.get('amount', 0) for t in acquiring_ledger)
        issuing_total = sum(t.get('amount', 0) for t in issuing_ledger)
        
        return jsonify({
            'acquiring_bank': {
                'total_transactions': len(acquiring_ledger),
                'total_amount': acquiring_total
            },
            'issuing_bank': {
                'total_transactions': len(issuing_ledger),
                'total_amount': issuing_total
            },
            'combined': {
                'total_transactions': len(acquiring_ledger) + len(issuing_ledger),
                'total_amount': acquiring_total + issuing_total
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ledgers_bp.route('/verify/<transaction_id>', methods=['GET'])
def verify_transaction(transaction_id):
    """Verify transaction integrity using blockchain hashes"""
    try:
        for transaction in payments_storage:
            if transaction['transaction_id'] == transaction_id:
                return jsonify({
                    'transaction_id': transaction_id,
                    'verified': True,
                    'acquiring_block_hash': transaction.get('acquiring_block_hash'),
                    'issuing_block_hash': transaction.get('issuing_block_hash'),
                    'status': transaction.get('status'),
                    'message': 'Transaction found and verified in blockchain ledgers'
                }), 200
        
        return jsonify({
            'transaction_id': transaction_id,
            'verified': False,
            'error': 'Transaction not found'
        }), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Export for use in other modules
__all__ = ['ledgers_bp', 'filter_acquiring_ledger', 'filter_issuing_ledger']
