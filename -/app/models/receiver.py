'''
Receiver / Merchant
the one who accepts NFC payment
'''
import uuid

from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db= SQLAlchemy()

class Receiver(db.Model):
    __tablename__ = 'receivers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    receiver_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    business_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

