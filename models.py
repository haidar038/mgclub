from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from datetime import datetime

from app_config import db, app

class User(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    role_id = db.Column(Integer, default=2)
    nama = db.Column(String(100), nullable=False)
    panggilan = db.Column(String(50), nullable=False)
    ktp = db.Column(String(18), unique=True, nullable=False)
    hp = db.Column(String(15), unique=True, nullable=False)
    sandi = db.Column(String(20), nullable=False)
    username = db.Column(String(100), unique=True, nullable=False)
    # Kolom baru untuk menyimpan foto profil
    profile_picture = db.Column(LargeBinary)

    card = db.relationship('Card', backref='user', uselist=False)

    def __repr__(self):
        return f"User('{self.nama}', '{self.panggilan}', '{self.ktp}', '{self.hp}', '{self.username}', '{self.card}')"
    
    def is_active(self):
        # Ubah logika ini sesuai kebutuhan Anda
        return True


class Admin(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    role_id = db.Column(Integer, default=1)
    nama = db.Column(String(100), nullable=False)
    email = db.Column(String(100), unique=True, nullable=False)
    sandi = db.Column(String(20), nullable=False)
    username = db.Column(String(100), unique=True, nullable=False)
    
    def is_active(self):
        # Ubah logika ini sesuai kebutuhan Anda
        return True
    
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(20), unique=True, nullable=False)
    poin = db.Column(db.Integer, default=0)
    scan_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Integer, nullable=False) 
    product_code = db.Column(db.String(20), unique=True, nullable=False)
    barcode_image = db.Column(db.Text) # Tambahkan kolom ini

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(20), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, default=0)
    final_price = db.Column(db.Integer, nullable=False)
    payment = db.Column(db.Integer, nullable=False)
    change = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
