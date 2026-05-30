"""
Payment Service
Handles payment processing business logic
"""

import uuid
import hashlib
from datetime import datetime
from app.services.smart_contract import default_smart_contract
from app.services.blockchain_service import acquiring_bank_ledger, issuing_bank_ledger


class PaymentProcessor:
    """Processes payment transactions through the payment flow"""
    
    def __init__(self):
        self.smart_contract = default_smart_contract
        self.acquiring_ledger = acquiring_bank_ledger
        self.issuing_ledger = issuing_bank_ledger
        self.transactions = {}
    
    def process_payment(self, user, merchant, amount):
        """
        Process payment transaction through complete flow
        
        Args:
            user (dict): User data with user_id, card_details
            merchant (dict): Merchant data with merchant_id
            amount (float): Payment amount
        
        Returns:
            dict: Transaction data with status
        """
        
        # Step 1: SIM Processing
        transaction = {
            'transaction_id': str(uuid.uuid4()),
            'user_id': user.get('user_id'),
            'merchant_id': merchant.get('merchant_id'),
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'card_details': user.get('card_details'),
            'status': None,
            'flow_type': 'payment'
        }
        
        print(f"[SIM] Initiating payment - {transaction['transaction_id']}")
        
        # Step 2: NFC Chip Processing
        print(f"[NFC Chip] Transmitting transaction to POS")
        
        # Step 3: Merchant POS Processing
        transaction['pos_status'] = 'received'
        print(f"[POS] Received and processing - {transaction['transaction_id']}")
        
        # Step 4: Smart Contract Validation
        is_valid, msg = self.smart_contract.validate_transaction(transaction)
        print(f"[Smart Contract] {msg}")
        
        if not is_valid:
            transaction['status'] = 'declined'
            transaction['decline_reason'] = msg
            self.transactions[transaction['transaction_id']] = transaction
            return transaction
        
        # Step 5: Acquiring Bank Processing
        transaction['acquiring_bank_status'] = 'processed'
        transaction['acquiring_block_hash'] = self._compute_hash(transaction)
        self.acquiring_ledger.add_transaction(transaction.copy())
        print(f"[Acquiring Bank] Processing - Hash: {transaction['acquiring_block_hash'][:16]}...")
        
        # Step 6: Card Scheme Processing
        transaction['card_scheme_status'] = 'routed'
        print(f"[Card Scheme] Routing to Issuing Bank")
        
        # Step 7: Issuing Bank Processing
        transaction['issuing_bank_status'] = 'authorized'
        transaction['issuing_block_hash'] = self._compute_hash(transaction)
        self.issuing_ledger.add_transaction(transaction.copy())
        print(f"[Issuing Bank] Validating - Hash: {transaction['issuing_block_hash'][:16]}...")
        
        # Step 8: Finalize
        transaction['status'] = 'completed'
        self.transactions[transaction['transaction_id']] = transaction
        
        print(f"[Payment Flow] Transaction completed successfully")
        
        return transaction
    
    def get_transaction(self, transaction_id):
        """Get transaction by ID"""
        return self.transactions.get(transaction_id)
    
    def get_all_transactions(self):
        """Get all transactions"""
        return list(self.transactions.values())
    
    def get_transactions_by_user(self, user_id):
        """Get all transactions for a user"""
        return [tx for tx in self.transactions.values() if tx.get('user_id') == user_id]
    
    def get_transactions_by_merchant(self, merchant_id):
        """Get all transactions for a merchant"""
        return [tx for tx in self.transactions.values() if tx.get('merchant_id') == merchant_id]
    
    def get_transactions_by_status(self, status):
        """Get all transactions with specific status"""
        return [tx for tx in self.transactions.values() if tx.get('status') == status]
    
    @staticmethod
    def _compute_hash(data):
        """Compute SHA256 hash of transaction"""
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()


# Global payment processor instance
payment_processor = PaymentProcessor()
