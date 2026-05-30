"""
Blockchain Service
Handles blockchain ledger operations
"""

import hashlib
from datetime import datetime


class BlockchainLedger:
    """Manages blockchain ledger for transactions"""
    
    def __init__(self, bank_name):
        self.bank_name = bank_name
        self.transactions = []
        self.chain = []
    
    def add_transaction(self, transaction):
        """
        Add transaction to ledger and blockchain
        
        Args:
            transaction (dict): Transaction data
        
        Returns:
            dict: Transaction with blockchain hash
        """
        # Compute block hash
        block_hash = self._compute_hash(transaction)
        transaction['block_hash'] = block_hash
        transaction['bank_name'] = self.bank_name
        transaction['added_at'] = datetime.now().isoformat()
        
        # Add to transactions list
        self.transactions.append(transaction)
        
        # Add to chain
        self.chain.append({
            'index': len(self.chain),
            'hash': block_hash,
            'previous_hash': self.chain[-1]['hash'] if self.chain else '0',
            'transaction': transaction
        })
        
        return transaction
    
    def get_all_transactions(self):
        """Get all transactions from ledger"""
        return self.transactions
    
    def get_transaction(self, transaction_id):
        """Get specific transaction by ID"""
        for tx in self.transactions:
            if tx.get('transaction_id') == transaction_id:
                return tx
        return None
    
    def get_ledger_summary(self):
        """Get ledger summary statistics"""
        total_transactions = len(self.transactions)
        total_amount = sum(tx.get('amount', 0) for tx in self.transactions)
        
        return {
            'bank_name': self.bank_name,
            'total_transactions': total_transactions,
            'total_amount': total_amount,
            'chain_length': len(self.chain),
            'created_at': datetime.now().isoformat()
        }
    
    def verify_chain_integrity(self):
        """Verify blockchain chain integrity"""
        for i, block in enumerate(self.chain):
            if i == 0:
                if block['previous_hash'] != '0':
                    return False, "Genesis block has invalid previous hash"
            else:
                if block['previous_hash'] != self.chain[i-1]['hash']:
                    return False, f"Block {i} has invalid previous hash"
            
            # Verify block hash
            computed_hash = self._compute_hash(block['transaction'])
            if computed_hash != block['hash']:
                return False, f"Block {i} hash mismatch"
        
        return True, "Blockchain chain is valid"
    
    @staticmethod
    def _compute_hash(data):
        """Compute SHA256 hash of data"""
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()


# Create ledger instances for Acquiring and Issuing Banks
acquiring_bank_ledger = BlockchainLedger('Acquiring Bank')
issuing_bank_ledger = BlockchainLedger('Issuing Bank')
