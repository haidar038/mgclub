from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime, Text, Enum
from datetime import datetime

from app_config import db, app

class User(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    role_id = db.Column(Integer, default=2)
    nama = db.Column(String(100), nullable=False, default='')
    email = db.Column(String(100), nullable=False)
    panggilan = db.Column(String(50), nullable=False, default='')
    ktp = db.Column(String(18), unique=True, nullable=False)
    hp = db.Column(String(15), unique=True, nullable=False)
    sandi = db.Column(String(20), nullable=False)
    username = db.Column(String(100), unique=True, nullable=False)
    profile_picture = db.Column(LargeBinary)
    #membership = db.Column(String(20), default='Silver')  # Kolom membership
    membership = db.Column(Enum('Silver', 'Gold', 'Platinum'), default='Silver') # Menggunakan Enum

    card = db.relationship('Card', backref='user', uselist=False)

    def __repr__(self):
        return f"User('{self.nama}', '{self.panggilan}', '{self.ktp}', '{self.hp}', '{self.username}', '{self.card}')"
    
    def is_active(self):
        return True
    
    @property
    def total_spending(self):
        # Menghitung total pembelanjaan user
        total = 0
        for transaction in self.card.transactions:
            total += transaction.final_price
        return total

class Admin(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    role_id = db.Column(Integer, default=1)
    nama = db.Column(String(100), nullable=False)
    email = db.Column(String(100), unique=True, nullable=False)
    sandi = db.Column(String(20), nullable=False)
    username = db.Column(String(100), unique=True, nullable=False)
    
    def is_active(self):
        return True
    
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(20), unique=True, nullable=False)
    poin = db.Column(db.Integer, default=0)
    scan_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    transactions = db.relationship('Transaction', backref='card', lazy='dynamic')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Integer, nullable=False) 
    product_code = db.Column(db.String(20), unique=True, nullable=False)
    barcode_image = db.Column(db.Text) 

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(20), db.ForeignKey('card.card_number'), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, default=0)
    final_price = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)  # Kolom untuk tanggal transaksi

    details = db.relationship('TransactionDetail', backref='transaction', cascade="all, delete-orphan")  # Relationship ke detail transaksi

class TransactionDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)  # Harga produk saat transaksi berlangsung

    product = db.relationship('Product')