"""
Smart Contract Service
Handles smart contract validation and execution
"""

from datetime import datetime


class SmartContract:
    """Smart contract that enforces transaction rules"""
    
    def __init__(self, max_amount=10000, valid_until="2025-12-31"):
        self.max_amount = max_amount
        self.valid_until = valid_until
    
    def validate_transaction(self, transaction_data):
        """
        Validate transaction against smart contract rules
        Args:
            transaction_data (dict):     Transaction data with amount, user_id, etc.
            Returns: tuple:              (bool, str) - (is_valid, message)
        """
        amount = transaction_data.get('amount', 0)
        
        # Check amount limit
        if amount <= 0:
            return False, "Amount must be greater than 0"
        
        if amount > self.max_amount:
            return False, f"Amount exceeds limit ({amount} > {self.max_amount})"
        
        # Check validity date
        try:
            valid_date = datetime.strptime(self.valid_until, "%Y-%m-%d")
            current_date = datetime.now()
            if current_date > valid_date:
                return False, "Smart contract has expired"
        except Exception as e:
            return False, f"Date validation error: {str(e)}"
        
        return True, "Transaction approved by smart contract"
    
    def get_config(self):
        """Get smart contract configuration"""
        return {
            'max_amount': self.max_amount,
            'valid_until': self.valid_until,
            'created_at': datetime.now().isoformat()
        }


# Default smart contract instance
default_smart_contract = SmartContract(
    max_amount=10000,
    valid_until="2025-12-31"
)
