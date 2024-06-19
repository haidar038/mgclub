from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime, Text, Enum
from datetime import datetime
from werkzeug.security import generate_password_hash

from app_config import db, app

class User(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    role_id = db.Column(Integer, default=2)
    nama = db.Column(String(100), nullable=False, default='')
    email = db.Column(String(100), nullable=False)
    panggilan = db.Column(String(50), nullable=False, default='')
    ktp = db.Column(String(18), unique=True, nullable=False)
    hp = db.Column(String(15), unique=True, nullable=False)
    sandi = db.Column(String(255), nullable=False)
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
        """Menghitung total pembelanjaan user."""
        if self.card:
            return sum(transaction.total_price for transaction in self.card.transactions)
        return 0  # Jika user belum memiliki kartu atau transaksi

    def update_membership(self):
        """Memperbarui membership berdasarkan total spending."""
        if self.total_spending >= 2000000:
            self.membership = 'Platinum'
        elif self.total_spending >= 500000:
            self.membership = 'Gold'
        else:
            self.membership = 'Silver'

    def reset_spending(self):
        """Mereset total spending dan memperbarui membership."""
        if self.card:
            self.card.transactions.delete()
            self.update_membership()  # Perbarui membership setelah reset
            db.session.commit()

class Admin(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    role_id = db.Column(Integer, default=1)
    nama = db.Column(String(100), nullable=False, default='Admin')
    email = db.Column(String(100), unique=True, nullable=False, default='')
    sandi = db.Column(String(255), nullable=False)
    username = db.Column(String(100), unique=True, nullable=False)
    
    def is_active(self):
        return True
    
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(20), unique=True, nullable=False)
    poin = db.Column(db.Integer, default=0)
    scan_count = db.Column(db.Integer, default=0)
    discount = db.Column(db.Integer, default=0)

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
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    details = db.relationship('TransactionDetail', backref='transaction', cascade="all, delete-orphan")

class TransactionDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product')

with app.app_context():
    db.create_all()

    if not Admin.query.first():
        supersu = Admin(username='admin', sandi=generate_password_hash('admin', method='pbkdf2'))
        db.session.add(supersu)
        db.session.commit()