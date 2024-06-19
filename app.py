from flask import render_template, session, request, redirect, flash, url_for, make_response, abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from barcode import Code128
from barcode.writer import ImageWriter
from werkzeug.utils import secure_filename

from models import User, Admin, Card, Product, Transaction, TransactionDetail  # Tambahkan TransactionDetail
from app_config import login_manager, db, bcrypt, app

import random, string, io, base64, qrcode, os, datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

with app.app_context():
    users = User.query.all()
    for user in users:
        # Logika untuk menentukan membership awal berdasarkan kriteria Anda
        if user.total_spending >= 2000000:
            user.membership = 'Platinum'
        elif user.total_spending >= 500000:
            user.membership = 'Gold'
        else:
            user.membership = 'Silver'
    db.session.commit()

# This function loads a user from the database.
@login_manager.user_loader
def load_user(user_id):
    """Loads a user from the database."""
    user = User.query.get(user_id)
    if user is not None:
        return user
    admin = Admin.query.get(user_id)
    if admin is not None:
        return admin
    return None

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role_id == 2:
            user = current_user
            card = Card.query.filter_by(user_id=user.id).first()

            # Generate QR Code 
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(card.card_number)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            qr_code_data = base64.b64encode(img_buffer.read()).decode()

            return render_template('index.html', user=current_user, card=card, cardnumber=qr_code_data, showQr=True)
        else:
            return redirect("/admin_dashboard")
    else:
        return redirect('/login')

@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):
    user = User.query.get_or_404(user_id)
    if user.profile_picture:
        response = make_response(user.profile_picture)
        response.headers.set('Content-Type', 'image/jpeg')  # Sesuaikan tipe konten jika perlu
        return response
    else:
        return app.send_static_file('images/default_profile.jpg')  # Ganti dengan path gambar default Anda

@app.route('/update_user_data/<int:id>', methods=['GET', 'POST'])
def update_user_data(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.hp = request.form['hp']
        user.panggilan = request.form['panggilan']
        user.ktp = request.form['ktp']
        user.nama = request.form['nama'] 
        db.session.commit()
        flash('Data berhasil diperbarui!', category='success')
        return redirect('/')
    else:
        return render_template('index.html', user=user)

@app.route('/update_password/<int:id>', methods=['GET', 'POST'])
def update_password(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if not bcrypt.check_password_hash(user.sandi, current_password):
            flash('Kata sandi saat ini tidak cocok.', category='danger')
            return render_template('index.html', user=user)
        if new_password != confirm_password:
            flash('Konfirmasi kata sandi tidak cocok.', category='danger')
            return render_template('index.html', user=user)
        user.sandi = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        flash('Password berhasil diperbarui!', category='success')
        return redirect('/')
    else:
        return render_template('index.html', user=user)

@app.route('/update_profile_picture/<int:user_id>', methods=['POST'])
@login_required
def update_profile_picture(user_id):
    user = User.query.get_or_404(user_id)
    if 'profile_picture' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('index'))

    file = request.files['profile_picture']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        # Hapus foto profil lama jika ada
        if user.profile_picture:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture))
            except Exception as e:
                print(f"Error deleting old profile picture: {e}")

        filename = secure_filename(file.filename)
        
        # Simpan gambar dalam variabel byte
        file_content = file.read()
        user.profile_picture = file_content
        db.session.commit()

        flash('Foto profil berhasil diperbarui!', 'success')
        return redirect(url_for('index'))

    else:
        flash('File yang diizinkan hanya JPG, JPEG, dan PNG.', 'danger')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        sandi = request.form['sandi']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.sandi, sandi):
            login_user(user)
            flash(f"Selamat Datang {user.nama}", category='success')
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
        email = request.form['emailaddress']
        hp = request.form['hp']
        ktp = request.form['ktp']
        sandi = request.form['sandi']
        username = generateusername()
        card_number = generate_card_number()
        poin = 0
        session['username'] = username

        if User.query.filter_by(hp=hp).first():
            flash('No. HP sudah ada!', category='warning')
            return render_template('register.html')
        else:
            hashed_password = bcrypt.generate_password_hash(sandi).decode('utf-8')
            user = User(hp=hp, sandi=hashed_password, ktp=ktp, username=username, email=email)
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

@app.route('/add_point/<int:id>', methods=['POST'])
def add_point(id):
    card = Card.query.get_or_404(id)
    if card:
        card.poin += 10  # Tambahkan 10 poin (sesuaikan dengan logika Anda)
        db.session.commit()
        flash('Poin berhasil ditambahkan!', category='success')
    else:
        flash('Kartu tidak ditemukan!', category='error')
    return redirect('/')  # Redirect kembali ke halaman dashboard

@app.route('/reset_point/<int:id>', methods=['POST'])
def reset_point(id):
    card = Card.query.get_or_404(id)
    if card:
        card.poin = 0  # Reset poin menjadi 0
        db.session.commit()
        flash('Poin berhasil direset!', category='success')
    else:
        flash('Kartu tidak ditemukan!', category='error')
    return redirect('/')  # Redirect kembali ke halaman dashboard

@app.route('/reset_spend/<int:user_id>', methods=['POST'])
def reset_spend(user_id):
    user = User.query.get_or_404(user_id)
    if user:
        user.reset_spending()
        flash('Total spending berhasil direset!', category='success')
    else:
        flash('User tidak ditemukan!', category='error')
    return redirect('/')  # Redirect kembali ke halaman dashboard

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

# ============= PRODUCT PAGE =============
def clean_numeric_value(value):
    return int(value.replace(".", "").replace(",", ""))

@app.route('/product_page', methods=['POST', 'GET'])
def product_page():
    product = Product.query.all()
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_code = request.form['product_code']
        
        product_price = clean_numeric_value(product_price)

        get_product = Product(product_name=product_name, product_price=product_price, product_code=product_code)
        db.session.add(get_product)
        db.session.commit()
        flash({'title':'Sukses!', 'message':'Produk berhasil dihapus'}, category='success')
        return redirect('product_page')
    else:
        encoded_image = []
        for prod in product:
            barcode = Code128(prod.product_code, writer=ImageWriter())
            buffer = io.BytesIO()
            barcode.write(buffer)
            buffer.seek(0)

            encoded_image = base64.b64encode(buffer.read()).decode('utf-8')
            # encoded_images.append(encoded_image)

        return render_template('admin/product_page.html', product=product, encoded_images=encoded_image)
        # return render_template('admin/product_page.html', product=product)

@app.route('/delete/<id>')
def delete_product(id):
    product = Product.query.get(id)

    db.session.delete(product)
    db.session.commit()

    flash({'title':'Peringatan!', 'message':'Produk berhasil dihapus'}, category='error')
    return redirect(url_for('product_page'))

# ============= KASIR PAGE ===============
@app.route('/cashier', methods=['GET', 'POST'])
def cashier():
    products = Product.query.all()
    return render_template('cashier.html', products=products)

from flask import request, redirect, flash
import json

# ... (kode lainnya di app.py)

@app.route('/process_transaction', methods=['POST'])
def process_transaction():
    card_number = request.form.get('card_number')
    transaction_data = request.form.get('transaction_data')
    card = Card.query.filter_by(card_number=card_number).first()

    try:
        transaction_data = json.loads(transaction_data)
        return render_template('transaction_confirmation.html', transaction_data=transaction_data)
    except Exception as e:
        flash('Format data transaksi tidak valid!', 'danger')
        return redirect('/cashier')

    # Hitung total harga
    total_price = 0
    for item in transaction_data:
        try:
            product_id, quantity = map(int, item.split('-'))
            product = Product.query.get(product_id)
            if product:
                total_price += product.product_price * quantity
            else:
                flash(f'Produk dengan ID {product_id} tidak ditemukan!', 'warning')
        except ValueError:
            flash('Format data produk tidak valid!', 'danger')
            return redirect('/cashier')

    # --- Proses Transaksi ---
    try:
        # Buat objek Transaction
        new_transaction = Transaction(card_number=card_number, total_price=total_price)
        db.session.add(new_transaction)
        db.session.commit()

        # Tambahkan detail 
        for item in transaction_data:
            product_id, quantity = map(int, item.split('-'))
            transaction_detail = TransactionDetail(
                transaction_id=new_transaction.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(transaction_detail)

        db.session.commit()

        # Kurangi poin pelanggan berdasarkan total belanja (opsional)
        # ... (logika untuk mengurangi poin)

        flash('Transaksi berhasil!', 'success')
        return redirect('/cashier')

    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {e}', 'danger')
        return redirect('/cashier')

@app.route('/check_card_discount/<card_number>', methods=['POST'])
def check_card_discount(card_number):
    card = Card.query.filter_by(card_number=card_number).first()
    if card:
        return jsonify({'exists': True, 'discount': card.discount})
    else:
        return jsonify({'exists': False, 'discount': 0})

@app.route('/check_product/<barcode>', methods=['POST'])
def check_product(barcode):
    product = Product.query.filter_by(product_code=barcode).first()
    if product:
        return jsonify({'success': True, 'product': {'id': product.id, 'name': product.product_name, 'price': product.product_price}})
    else:
        return jsonify({'success': False})

@app.route('/check_card/<card_number>', methods=['POST'])
def check_card(card_number):
    card = Card.query.filter_by(card_number=card_number).first()
    if card:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

# ============= ADD PRODUCT PAGE ===============
def generate_product_code(length=8):
    """Generate kode produk unik yang tidak ada di database."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Product.query.filter_by(product_code=code).first():
            return code

@app.route('/add_product', methods=['GET', 'POST'])
# @login_required
def add_product():
    # if current_user.role_id != 1: 
    #     abort(403)
    products = Product.query.all()

    if request.method == 'POST':
        product_name = request.form['product_name']
        product_price = request.form['product_price']

        # Generate kode produk unik
        product_code = generate_product_code()

        # Generate barcode
        barcode = Code128(product_code, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode.write(buffer)
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.read()).decode('utf-8')

        new_product = Product(
            product_name=product_name, 
            product_price=product_price, 
            product_code=product_code,
            barcode_image=encoded_image
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Produk berhasil ditambahkan!', 'success')
        return render_template('add_product.html', new_product=new_product, products=products) 

    return render_template('add_product.html', products=products)

if __name__ == '__main__':
    app.run(debug=True, port=5000)