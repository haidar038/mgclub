from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from app_config import db

class User(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    role_id = db.Column(Integer, default=2)
    nama = db.Column(String(100), nullable=False)
    panggilan = db.Column(String(50), nullable=False)
    ktp = db.Column(String(18), unique=True, nullable=False)
    hp = db.Column(String(15), unique=True, nullable=False)
    sandi = db.Column(String(20), nullable=False)
    username = db.Column(String(100), unique=True, nullable=False)

    card = relationship('Card', back_populates='user')

    def __repr__(self):
        return f"User('{self.nama}', '{self.panggilan}', '{self.ktp}', '{self.hp}', '{self.username}', '{self.card}')"
    
    def is_active(self):
        # Ubah logika ini sesuai kebutuhan Anda
        return True

class Card(db.Model):
    id = db.Column(Integer, primary_key=True)
    card_number = db.Column(String(20), unique=True, nullable=False)
    poin = db.Column(Integer, default=0, nullable=False)
    user_id = db.Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='card')

    def __repr__(self):
        return f"Card('{self.card_number}', '{self.poin}', '{self.user_id}')"

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
    
class Product(db.Model):
    id = db.Column(Integer, primary_key=True)
    product_name = db.Column(String(100), nullable=False)
    product_price = db.Column(Integer, nullable=False)
    product_code = db.Column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.product_name}', '{self.product_price}', '{self.product_code}')"
# class Server(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     harga = db.Column(db.String(100))
#     poin = db.Column(db.String(20))
    
#     def is_active(self):
#         # Ubah logika ini sesuai kebutuhan Anda
#         return True