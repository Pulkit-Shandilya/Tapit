from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import *


db = SQLAlchemy()

    
class Transaction(db.Model):
    __tablename__ = 'transactions'


id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))