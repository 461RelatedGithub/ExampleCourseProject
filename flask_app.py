from flask import Flask, render_template, request, session, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key'
app.config['DEBUG'] = True

def get_db_connection():
    conn = sqlite3.connect('test.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.before_first_request
def initialize_database():
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS products')
        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('DROP TABLE IF EXISTS receipts')

        # products table
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                image_url TEXT
            );
        ''')

        # users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                address_line1 TEXT,
                address_line2 TEXT,
                city TEXT,
                state TEXT,
                postal_code TEXT,
                country TEXT
            );
        ''')

        # receipts table
        cursor.execute('''
            CREATE TABLE receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                items TEXT NOT NULL,
                total_price REAL NOT NULL,
                address_line1 TEXT,
                address_line2 TEXT,
                city TEXT,
                state TEXT,
                postal_code TEXT,
                country TEXT,
                card_number TEXT,
                expiration_date TEXT,
                cvv TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')


        # example products with image URLs
        example_products = [
            ('Handmade Ceramic Mug', 'Home & Living', 20.95, 'https://images.pexels.com/photos/4065905/pexels-photo-4065905.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Personalized Sweatshirt', 'Clothing', 25.65, 'https://images.pexels.com/photos/189199/pexels-photo-189199.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Emerald Earrings', 'Jewelry', 36.40, 'https://images.pexels.com/photos/17298627/pexels-photo-17298627/free-photo-of-genuine-earring-with-diamonds-and-emeralds.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('14 K Gold Chain Necklace', 'Jewelry', 95.00, 'https://images.pexels.com/photos/2703907/pexels-photo-2703907.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Custom Baby Onesie', 'Baby', 15.75, 'https://images.pexels.com/photos/6849303/pexels-photo-6849303.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Vintage Record Player', 'Electronics & Accessories', 120.49, 'https://images.pexels.com/photos/775414/pexels-photo-775414.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Leather Tote Bag', 'Bags & Purses', 80.35, 'https://images.pexels.com/photos/20399717/pexels-photo-20399717/free-photo-of-bag-on-wicker-chair.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Organic Bath Bombs', 'Bath & Beauty', 12.99, 'https://images.pexels.com/photos/6620948/pexels-photo-6620948.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Watercolor Painting', 'Art & Collectibles', 45.00, 'https://images.pexels.com/photos/1286632/pexels-photo-1286632.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Handmade Journal', 'Books, Movies & Music', 30.75, 'https://images.pexels.com/photos/1765033/pexels-photo-1765033.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('DIY Craft Kit', 'Craft Supplies & Tools', 20.50, 'https://images.pexels.com/photos/7585704/pexels-photo-7585704.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Decorative Throw Pillow', 'Home & Living', 35.99, 'https://images.pexels.com/photos/7319279/pexels-photo-7319279.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Handmade Soap', 'Bath & Beauty', 8.99, 'https://images.pexels.com/photos/7500307/pexels-photo-7500307.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Personalized Bracelet', 'Jewelry', 25.45, 'https://images.pexels.com/photos/4993282/pexels-photo-4993282.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Customized Phone Case', 'Electronics & Accessories', 18.20, 'https://images.pexels.com/photos/3392232/pexels-photo-3392232.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Knitted Scarf', 'Clothing', 20.89, 'https://images.pexels.com/photos/5603012/pexels-photo-5603012.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Wooden Toy Train', 'Toys', 40.25, 'https://images.pexels.com/photos/14739171/pexels-photo-14739171.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Soy Scented Candle', 'Home & Living', 15.50, 'https://images.pexels.com/photos/13920421/pexels-photo-13920421.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Hand-stitched Notebook', 'Books, Movies & Music', 12.30, 'https://images.pexels.com/photos/461435/pexels-photo-461435.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Hand-painted Canvas', 'Art & Collectibles', 100.00, 'https://images.pexels.com/photos/4483109/pexels-photo-4483109.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Baby Blanket', 'Baby', 25.35, 'https://images.pexels.com/photos/4887108/pexels-photo-4887108.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Leather Wallet', 'Bags & Purses', 50.00, 'https://images.pexels.com/photos/4452401/pexels-photo-4452401.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Facial Scrub', 'Bath & Beauty', 10.75, 'https://images.pexels.com/photos/6977992/pexels-photo-6977992.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Crystal Pendant Necklace', 'Jewelry', 55.99, 'https://images.pexels.com/photos/12486656/pexels-photo-12486656.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Vintage Camera', 'Electronics & Accessories', 200.00, 'https://images.pexels.com/photos/2787216/pexels-photo-2787216.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Custom Portrait', 'Art & Collectibles', 75.45, 'https://images.pexels.com/photos/20401426/pexels-photo-20401426/free-photo-of-woman-with-blonde-hair.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Eco-Friendly Notebooks', 'Books, Movies & Music', 15.89, 'https://images.pexels.com/photos/20358835/pexels-photo-20358835/free-photo-of-close-up-of-notebooks-with-patterned-paper-edges.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Artisan Coffee Mug', 'Home & Living', 25.50, 'https://images.pexels.com/photos/3563623/pexels-photo-3563623.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Wooden Puzzle', 'Toys', 20.15, 'https://images.pexels.com/photos/7269615/pexels-photo-7269615.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Herbal Bath Salts', 'Bath & Beauty', 12.49, 'https://images.pexels.com/photos/7356379/pexels-photo-7356379.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Gold Hoop Earrings', 'Jewelry', 45.75, 'https://images.pexels.com/photos/12144842/pexels-photo-12144842.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Macrame Wall Hanging', 'Home & Living', 50.00, 'https://images.pexels.com/photos/16820437/pexels-photo-16820437/free-photo-of-a-handmade-macrame-hanging-on-the-wall.jpeg?auto=compress&cs=tinysrgb&w=600'),
            ('Crochet Baby Hat', 'Baby', 10.25, 'https://images.pexels.com/photos/20396272/pexels-photo-20396272/free-photo-of-baby-holding-finger-in-mouth.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Beaded Necklace', 'Accessories', 22.75, 'https://images.pexels.com/photos/8334684/pexels-photo-8334684.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Leather Belt', 'Accessories', 30.99, 'https://images.pexels.com/photos/19046442/pexels-photo-19046442/free-photo-of-woman-in-brown-standing-by-green-wooden-door.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Handmade Earrings', 'Accessories', 18.50, 'https://images.pexels.com/photos/8774769/pexels-photo-8774769.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Antique Painting', 'Art & Collectibles', 150.00, 'https://images.pexels.com/photos/1767017/pexels-photo-1767017.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Vintage Toy Car', 'Art & Collectibles', 60.35, 'https://images.pexels.com/photos/149406/pexels-photo-149406.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Baby Shoes', 'Baby', 20.00, 'https://images.pexels.com/photos/3965503/pexels-photo-3965503.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Vintage Bucket Hat', 'Accessories', 35.50, 'https://images.pexels.com/photos/2976291/pexels-photo-2976291.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Canvas Tote Bag', 'Bags & Purses', 40.00, 'https://images.pexels.com/photos/19517458/pexels-photo-19517458/free-photo-of-tote-bag-by-the-tree-in-a-park.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Silk Scarf', 'Bags & Purses', 30.49, 'https://images.pexels.com/photos/12471946/pexels-photo-12471946.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Natural Lip Balm', 'Bath & Beauty', 5.99, 'https://images.pexels.com/photos/374856/pexels-photo-374856.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Handmade Lotion', 'Bath & Beauty', 15.75, 'https://images.pexels.com/photos/1029896/pexels-photo-1029896.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Chronicles of Narnia Collection', 'Books, Movies & Music', 22.95, 'https://images.pexels.com/photos/159778/books-reading-series-narnia-159778.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Vinyl Record', 'Books, Movies & Music', 25.35, 'https://images.pexels.com/photos/2746823/pexels-photo-2746823.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Sketchbook', 'Books, Movies & Music', 10.50, 'https://images.pexels.com/photos/826114/pexels-photo-826114.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Watercolor Set', 'Craft Supplies & Tools', 25.45, 'https://images.pexels.com/photos/6487216/pexels-photo-6487216.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Sewing Kit', 'Craft Supplies & Tools', 18.75, 'https://images.pexels.com/photos/19496818/pexels-photo-19496818/free-photo-of-a-sewing-kit.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Stamp Seal Kit', 'Craft Supplies & Tools', 15.99, 'https://images.pexels.com/photos/19216748/pexels-photo-19216748/free-photo-of-stamp-seal-and-coins.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Wireless Headphones', 'Electronics & Accessories', 150.00, 'https://images.pexels.com/photos/610945/pexels-photo-610945.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Portable Charger', 'Electronics & Accessories', 35.25, 'https://images.pexels.com/photos/4526425/pexels-photo-4526425.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Gift Box', 'Gifts', 30.99, 'https://images.pexels.com/photos/264985/pexels-photo-264985.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Personalized Mug', 'Gifts', 20.50, 'https://images.pexels.com/photos/1755215/pexels-photo-1755215.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Greeting Cards', 'Gifts', 10.75, 'https://images.pexels.com/photos/8715582/pexels-photo-8715582.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Throw Blanket', 'Home & Living', 45.00, 'https://images.pexels.com/photos/5603255/pexels-photo-5603255.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
            ('Ceramic Plate Set', 'Home & Living', 60.95, 'https://images.pexels.com/photos/6794575/pexels-photo-6794575.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1')
        ]

        cursor.executemany('INSERT INTO products (name, category, price, image_url) VALUES (?, ?, ?, ?)', example_products)

        conn.commit()
        conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db_connection()
    cursor = db.cursor()

    search_term = ''
    selected_category = ''
    items = []

    if request.method == "POST":
        search_term = request.form.get('search', '')
        selected_category = request.form.get('category', '')

        if search_term and selected_category:
            items = cursor.execute("SELECT * FROM products WHERE (name LIKE ? OR category LIKE ?) AND category = ?", ('%' + search_term + '%', '%' + search_term + '%', selected_category)).fetchall()
        elif search_term:
            items = cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", ('%' + search_term + '%', '%' + search_term + '%')).fetchall()
        elif selected_category:
            items = cursor.execute("SELECT * FROM products WHERE category = ?", (selected_category,)).fetchall()
        else:
            items = cursor.execute("SELECT * FROM products").fetchall()
    else:
        items = cursor.execute("SELECT * FROM products").fetchall()

    db.close()
    return render_template("main_page.html", items=items)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    db = get_db_connection()
    cursor = db.cursor()
    product = cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    db.close()
    return render_template("product.html", product=product)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if 'cart' not in session:
        session['cart'] = {}

    if product_id in session['cart']:
        session['cart'][product_id] += quantity
    else:
        session['cart'][product_id] = quantity

    session.modified = True
    flash('Product added to cart!')
    return redirect(url_for('index'))

@app.route("/clear_cart")
def clear_cart():
    session.pop('cart', None)
    flash('Cart cleared!', 'info')
    return redirect(url_for('view_cart'))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if 'username' not in session:
        flash('You need to be logged in to checkout', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        db = get_db_connection()
        cursor = db.cursor()

        items = []
        total_price = 0

        for product_id, quantity in session.get('cart', {}).items():
            product = cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if product:
                total_price += product['price'] * quantity
                items.append(f"{quantity} x {product['name']}")

        items_str = ', '.join(items)

        # Capture shipping address and credit card information
        address_line1 = request.form.get('address_line1', '')
        address_line2 = request.form.get('address_line2', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        postal_code = request.form.get('postal_code', '')
        country = request.form.get('country', '')

        card_number = request.form.get('card_number', '')
        expiration_date = request.form.get('expiration_date', '')
        cvv = request.form.get('cvv', '')

        # Insert receipt into the database (without card details)
        cursor.execute('''
            INSERT INTO receipts (username, items, total_price, address_line1, address_line2, city, state, postal_code, country)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['username'], items_str, total_price, address_line1, address_line2, city, state, postal_code, country))
        db.commit()
        db.close()

        session.pop('cart', None)
        flash('Thank you for your purchase! Your order has been placed.', 'success')
        return render_template("receipt.html", items=items, total_price=total_price, address_line1=address_line1, address_line2=address_line2, city=city, state=state, postal_code=postal_code, country=country)

    # Render checkout form if it's a GET request
    return render_template("checkout.html")







@app.route("/cart")
def view_cart():
    db = get_db_connection()
    cursor = db.cursor()
    items = []
    total_price = 0

    for product_id, quantity in session.get('cart', {}).items():
        product = cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if product:
            total_price += product['price'] * quantity
            items.append({'name': product['name'], 'quantity': quantity, 'price': product['price']})

    db.close()
    return render_template("cart.html", items=items, total_price=total_price)

@app.route("/history")
def view_history():
    if 'username' not in session:
        flash('You need to be logged in to view purchase history', 'danger')
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()
    receipts = cursor.execute("SELECT * FROM receipts WHERE username = ?", (session['username'],)).fetchall()
    db.close()
    return render_template("history.html", receipts=receipts)

@app.route("/clear_history")
def clear_history():
    if 'username' not in session:
        flash('You need to be logged in to clear purchase history', 'danger')
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM receipts WHERE username = ?", (session['username'],))
    db.commit()
    db.close()
    flash('Purchase history cleared!', 'info')
    return redirect(url_for('view_history'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        address_line1 = request.form.get('address_line1', '')
        address_line2 = request.form.get('address_line2', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        postal_code = request.form.get('postal_code', '')
        country = request.form.get('country', '')
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password, address_line1, address_line2, city, state, postal_code, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, address_line1, address_line2, city, state, postal_code, country))
            db.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken', 'danger')
        finally:
            db.close()
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db_connection()
        cursor = db.cursor()
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        db.close()
        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()
