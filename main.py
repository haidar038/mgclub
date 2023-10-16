from flask import Flask, render_template, request, redirect, flash, session
from flask_login import current_user, login_user, logout_user, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_qrcode import QRcode
import random, string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'mg.club'

db = SQLAlchemy(app)
qrcode = QRcode(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    panggilan = db.Column(db.String(50))
    ktp = db.Column(db.String(18), unique=True)
    hp = db.Column(db.String(15), unique=True)
    sandi = db.Column(db.String(20))
    username = db.Column(db.String(100))
    card_number = db.Column(db.String(20))
    poin = db.Column(db.Integer, default=0)
    # poin = db.relationship('Card', backref='user')
    
    def is_active(self):
        return True  # Ubah logika ini sesuai kebutuhan Anda

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    email = db.Column(db.String(100))
    sandi = db.Column(db.String(20))
    username = db.Column(db.String(100))
    
    def is_active(self):
        return True  # Ubah logika ini sesuai kebutuhan Anda

class Server(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    harga = db.Column(db.String(100))
    poin = db.Column(db.String(20))
    
    def is_active(self):
        return True  # Ubah logika ini sesuai kebutuhan Anda
    
# class Card(db.Model):
#     __tablename__ = 'card'
#     card_number = db.Column(db.String(20))
#     poin = db.Column(db.Integer, default=0)
#     id = db.Column(db.Integer, primary_key=True)
    
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


login_manager = LoginManager()
login_manager.init_app(app)

def generateusername():
    while True:
        username = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        existing_usernames = User.query.filter_by(username=username).all()
        if username not in existing_usernames:
            return username

def generate_card_number():
    while True:
        card_number = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        existing_card_numbers = User.query.filter_by(card_number=card_number).all()
        if card_number not in existing_card_numbers:
            return card_number

# This function loads a user from the database.
@login_manager.user_loader
def load_user(user_id):
    """Loads a user from the database."""
    return User.query.get(user_id)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    if current_user.is_authenticated:
        user = current_user
        return render_template('index.html', user=user)
    else:
        return redirect('/login')

@app.route("/profil")
def profil():
    if current_user.is_authenticated:
        user = current_user
        return render_template('profil.html', user=user)
    else:
        return redirect('/login')
    
@app.route("/profile_update")
def update():
    if current_user.is_authenticated:
        user = current_user
        return render_template('update.html', user=user)
    else:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        sandi = request.form['sandi']
        
        user = User.query.filter_by(username=username).first()
        if user and user.sandi == sandi:
            login_user(user)
            return redirect('/')
        else:
            flash("Periksa Username atau Kata Sandi", category='danger')
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hp = request.form['hp']
        sandi = request.form['sandi']
        panggilan = request.form['panggilan']
        ktp = request.form['ktp']
        nama = request.form['fullname']
        username = generateusername()
        card_number = generate_card_number()
        poin = 0
        session['username'] = username

        if User.query.filter_by(hp=hp).first():
            flash('No. HP sudah ada!', category='warning')
            return render_template('register.html')
        else:
            user = User(hp=hp, sandi=sandi, panggilan=panggilan, ktp=ktp, nama=nama, username=username, card_number=card_number, poin=poin)
            db.session.add(user)
            db.session.commit()
            return redirect('/register_success')
    else:
        return render_template('register.html')
    
@app.route('/register_success')
def register_success():
    username = session.get('username')
    return render_template("username.html", username=username)

def update_user_data(username, nama, panggilan, ktp, hp, sandi):
    user = User.query.filter_by(username=username).first()
    if user:
        user.nama = nama
        user.panggilan = panggilan
        user.ktp = ktp
        user.hp = hp
        user.sandi = sandi
        db.session.commit()
    else:
        return
    
@app.route('/update_user_data/<int:id>', methods=['GET', 'POST'])
def update_user_data(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.hp = request.form['hp']
        user.sandi = request.form['sandi']
        user.panggilan = request.form['panggilan']
        user.ktp = request.form['ktp']
        user.nama = request.form['nama']
        db.session.commit()
        flash('Data berhasil diperbarui!', category='success')
        return redirect('/profil')
    else:
        user_data = User.query.filter_by(username=current_user.username).first()
        return render_template('update.html', user_data=user_data)

def add_point(poin, username):
    user = User.query.filter_by(username=username).first()
    poin = 10
    if user:
        user.poin = poin
        db.session.commit()
    else:
        return

@app.route('/add_point/<int:id>', methods=['GET', 'POST'])
def add_point(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.poin = user.poin+10
        db.session.commit()
        flash('Poin berhasil diperbarui!', category='success')
        return redirect('/')
    else:
        user_data = User.query.filter_by(username=current_user.username).first()
        return render_template('index.html', user_data=user_data)

def reset_point(poin, username):
    user = User.query.filter_by(username=username).first()
    poin = 0
    if user:
        user.poin = poin
        db.session.commit()
    else:
        return
    
@app.route('/reset_point/<int:id>', methods=['GET', 'POST'])
def reset_point(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.poin = 0
        db.session.commit()
        flash('Poin berhasil diperbarui!', category='success')
        return redirect('/')
    else:
        user_data = User.query.filter_by(username=current_user.username).first()
        return render_template('index.html', user_data=user_data)

# ============= ADMIN SECTION ============
@app.route('/admin_dashboard')
def admin_dashboard():
    user = User.query.all()
    if current_user.is_authenticated:
        return render_template('admin/index.html', user_data=user)
    else:
        return redirect('/admin_login')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        sandi = request.form['sandi']

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.sandi == sandi:
            login_user(admin)
            return redirect('admin_dashboard')
        else:
            flash("Periksa Username atau Kata Sandi", category='danger')
            return render_template('admin/login.html')
    else:
        return render_template('admin/login.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        sandi = request.form['sandi']
        email = request.form['email']
        nama = request.form['nama']
        username = request.form['username']

        if Admin.query.filter_by(email=email).first():
            flash('Email sudah terdaftar, gunakan email yang lain!', category='warning')
            return render_template('admin/register.html')
        else:
            admin = Admin(sandi=sandi, nama=nama, username=username, email=email)
            db.session.add(admin)
            db.session.commit()
            return redirect('admin_dashboard')
    else:
        return render_template('admin/register.html')
    
@app.route('/admin_logout')
def admin_logout():
    logout_user()
    return redirect('admin_login')

# ============= SERVER SIDE ===============

@app.route('/redirect_point/<int:points>', methods=['GET', 'POST'])
def redirect_point(points):
    server_point = Server.query.get_or_404(points)
    if request.method == 'POST':
        server_point.poin = request.form['poin']
        db.session.commit()
    else:
        return

if __name__ == '__main__':
    app.run(debug=True)
