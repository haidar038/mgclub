from flask import render_template, session, request, redirect, flash
from flask_login import current_user, login_user, logout_user
from barcode import Code128, generate
from barcode.writer import ImageWriter

from models import User, Admin, Card, Product
from app_config import login_manager, db, bcrypt, app

import random, string, io, base64

def generateusername():
    while True:
        username = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        existing_usernames = User.query.filter_by(username=username).all()
        if username not in existing_usernames:
            return username

def generate_card_number():
    while True:
        card_number = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        existing_card_numbers = Card.query.filter_by(card_number=card_number).all()
        if card_number not in existing_card_numbers:
            return card_number

# This function loads a user from the database.
@login_manager.user_loader
def load_user(role_id):
    """Loads a user from the database."""
    admin = Admin.query.filter_by(role_id=1).first()
    user = User.query.filter_by(role_id=2).first()
    if admin:
        return Admin.query.get(role_id)
    elif user:
        return User.query.get(role_id)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role_id == 2:
            user = current_user
            card = Card.query.filter_by(user_id=user.id).first()
            return render_template('index.html', user=user, card=card)
        else:
            return redirect("/admin_dashboard")
    else:
        return redirect('/login')

@app.route("/profil")
def profil():
    if current_user.is_authenticated:
        user = current_user
        card = Card.query.filter_by(user_id=user.id).first()

        # Generate barcode
        cardnumber = Code128(card.card_number, writer=ImageWriter())
        buffer = io.BytesIO()
        cardnumber.write(buffer)
        buffer.seek(0)
        
        # Encode barcode image to base64
        encoded_image = base64.b64encode(buffer.read()).decode('utf-8')
        
        return render_template('profil.html', user=user, card=card, cardnumber=encoded_image)
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
        if user and bcrypt.check_password_hash(user.sandi, sandi):
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
            hashed_password = bcrypt.generate_password_hash(sandi).decode('utf-8')
            user = User(hp=hp, sandi=hashed_password, panggilan=panggilan, ktp=ktp, nama=nama, username=username)
            db.session.add(user)
            db.session.commit()
            user_card = Card(card_number=card_number, poin=poin, user_id=user.id)
            db.session.add(user_card)
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

@app.route('/add_point/<int:id>', methods=['GET', 'POST'])
def add_point(id):
    user_card = Card.query.get_or_404(id)
    if request.method == 'POST':
        user_card.poin = user_card.poin+10
        db.session.commit()
        return redirect('/')
    
@app.route('/reset_point/<int:id>', methods=['GET', 'POST'])
def reset_point(id):
    user_card = Card.query.get_or_404(id)
    if request.method == 'POST':
        user_card.poin = 0
        db.session.commit()
        return redirect('/')

# ============= ADMIN SECTION ============
@app.route('/admin_dashboard')
def admin_dashboard():
    user = User.query.all()
    user_total = db.session.query(User).count()
    if current_user.is_authenticated:
        admin = Admin.query.filter_by(role_id=1).first()
        if admin:
            return render_template('admin/index.html', user_data=user, admin=current_user, total=user_total)
        else:
            return redirect("/")
    else:
        return redirect('/admin_login')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        sandi = request.form['sandi']

        admin = Admin.query.filter_by(username=username).first()
        if admin and bcrypt.check_password_hash(admin.sandi, sandi):
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
            hashed_password = bcrypt.generate_password_hash(sandi).decode('utf-8')
            admin = Admin(sandi=hashed_password, nama=nama, username=username, email=email)
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

# @app.route('/redirect_point/<int:points>', methods=['GET', 'POST'])
# def redirect_point(points):
#     server_point = Server.query.get_or_404(points)
#     if request.method == 'POST':
#         server_point.poin = request.form['poin']
#         db.session.commit()
#     else:
#         return

# ============= PRODUCT PAGE =============
@app.route('/product_page', methods=['POST', 'GET'])
def product_page():
    product = Product.query.all()
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_code = request.form['product_code']
        
        get_product = Product(product_name=product_name, product_price=product_price, product_code=product_code)
        db.session.add(get_product)
        db.session.commit()
        flash("Produk berhasil ditambahkan", category='success')
        return redirect('product_page')
    else:
        return render_template('admin/product_page.html', product=product)


if __name__ == '__main__':
    app.run(debug=True, port=5000)