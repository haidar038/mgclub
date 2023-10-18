from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from mgclub import db

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, default=2)
    nama = Column(String(100))
    panggilan = Column(String(50))
    ktp = Column(String(18), unique=True)
    hp = Column(String(15), unique=True)
    sandi = Column(String(20))
    username = Column(String(100), unique=True)

    card = relationship('Card', back_populates='user')

    def __repr__(self):
        return f"User('{self.nama}', '{self.panggilan}', '{self.ktp}', '{self.hp}', '{self.username}', '{self.card}')"
    
    def is_active(self):
        # Ubah logika ini sesuai kebutuhan Anda
        return True

class Card(db.Model):
    id = Column(Integer, primary_key=True)
    card_number = Column(String(20), unique=True)
    poin = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='card')

    def __repr__(self):
        return f"Card('{self.card_number}', '{self.poin}', '{self.user_id}')"

class Admin(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, default=1)
    nama = Column(String(100))
    email = Column(String(100), unique=True)
    sandi = Column(String(20))
    username = Column(String(100), unique=True)
    
    def is_active(self):
        # Ubah logika ini sesuai kebutuhan Anda
        return True

# class Server(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     harga = db.Column(db.String(100))
#     poin = db.Column(db.String(20))
    
#     def is_active(self):
#         # Ubah logika ini sesuai kebutuhan Anda
#         return True