"""
Payment Model
Represents persisted payment history records.
"""

from datetime import datetime
import uuid

from app import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    from_user_id = db.Column(db.String(50), nullable=True, index=True)
    to_user_id = db.Column(db.String(50), nullable=True, index=True)
    user_id = db.Column(db.String(50), nullable=True, index=True)
    merchant_id = db.Column(db.String(50), nullable=True, index=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='completed', index=True)
    flow_type = db.Column(db.String(30), nullable=False, index=True)
    note = db.Column(db.String(255))
    block_hash = db.Column(db.String(128))
    acquiring_bank_status = db.Column(db.String(30))
    issuing_bank_status = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'from_user_id': self.from_user_id,
            'to_user_id': self.to_user_id,
            'user_id': self.user_id,
            'merchant_id': self.merchant_id,
            'amount': self.amount,
            'status': self.status,
            'flow_type': self.flow_type,
            'note': self.note,
            'block_hash': self.block_hash,
            'acquiring_bank_status': self.acquiring_bank_status,
            'issuing_bank_status': self.issuing_bank_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }