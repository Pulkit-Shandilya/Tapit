"""
Authentication Service
Handles user authentication and authorization
"""

import uuid
import hashlib
from datetime import datetime
from app.services.smart_contract import default_smart_contract
from app.services.blockchain_service import issuing_bank_ledger


class AuthorizationProcessor:
    """Processes authorization transactions"""
    
    def __init__(self):
        self.smart_contract = default_smart_contract
        self.issuing_ledger = issuing_bank_ledger
        self.authorizations = {}
    
    def authorize_transaction(self, user, amount):
        """
        Process authorization transaction through authorization flow
        
        Args:
            user (dict): User data with user_id, card_details
            amount (float): Authorization amount
        
        Returns:
            dict: Authorization data with status
        """
        
        # Step 1: SIM Processing
        authorization = {
            'transaction_id': str(uuid.uuid4()),
            'user_id': user.get('user_id'),
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'card_details': user.get('card_details'),
            'status': None,
            'flow_type': 'authorization'
        }
        
        print(f"[SIM] Initiating authorization - {authorization['transaction_id']}")
        
        # Step 2: BaseBand Processing
        authorization['emulation_status'] = 'emulated'
        print(f"[BaseBand] Emulating POS - {authorization['transaction_id']}")
        
        # Step 3: OTA Platform Processing
        authorization['ota_status'] = 'processed'
        print(f"[OTA Platform] Processing authorization")
        
        # Step 4: Smart Contract Validation
        is_valid, msg = self.smart_contract.validate_transaction(authorization)
        print(f"[Smart Contract] {msg}")
        
        if not is_valid:
            authorization['status'] = 'declined'
            authorization['decline_reason'] = msg
            self.authorizations[authorization['transaction_id']] = authorization
            return authorization
        
        # Step 5: Issuing Bank Processing
        authorization['issuing_bank_status'] = 'authorized'
        authorization['issuing_block_hash'] = self._compute_hash(authorization)
        self.issuing_ledger.add_transaction(authorization.copy())
        print(f"[Issuing Bank] Validating - Hash: {authorization['issuing_block_hash'][:16]}...")
        
        # Step 6: Finalize
        authorization['status'] = 'authorized'
        self.authorizations[authorization['transaction_id']] = authorization
        
        print(f"[Authorization Flow] Transaction authorized successfully")
        
        return authorization
    
    def get_authorization(self, transaction_id):
        """Get authorization by ID"""
        return self.authorizations.get(transaction_id)
    
    def get_all_authorizations(self):
        """Get all authorizations"""
        return list(self.authorizations.values())
    
    def get_authorizations_by_user(self, user_id):
        """Get all authorizations for a user"""
        return [auth for auth in self.authorizations.values() if auth.get('user_id') == user_id]
    
    def get_authorizations_by_status(self, status):
        """Get all authorizations with specific status"""
        return [auth for auth in self.authorizations.values() if auth.get('status') == status]
    
    @staticmethod
    def _compute_hash(data):
        """Compute SHA256 hash of authorization"""
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()


# Global authorization processor instance
authorization_processor = AuthorizationProcessor()
