from flask import Flask
from flask_qrcode import QRcode
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_toastr import Toastr

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mgclub.db'
app.config['SECRET_KEY'] = 'mg.club'

login_manager = LoginManager()
bcrypt = Bcrypt()
db = SQLAlchemy()
qrcode = QRcode()
toastr = Toastr()

login_manager.init_app(app)
db.init_app(app)
bcrypt.init_app(app)
qrcode.init_app(app)
toastr.init_app(app)