from flask import Flask
from flask_qrcode import QRcode
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_toastr import Toastr
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'mg.club') # Gunakan variabel environment atau nilai default
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.environ.get("MYSQLUSER")}:{os.environ.get("MYSQLPASSWORD")}@{os.environ.get("MYSQLHOST")}:{os.environ.get("MYSQLPORT")}/{os.environ.get("MYSQLDATABASE")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
bcrypt = Bcrypt()
db = SQLAlchemy()
qrcode = QRcode()
toastr = Toastr()
migrate = Migrate(app, db)

login_manager.init_app(app)
db.init_app(app)
bcrypt.init_app(app)
qrcode.init_app(app)
toastr.init_app(app)

UPLOAD_FOLDER = 'static/uploads/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Membuat folder jika belum ada