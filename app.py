from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)

# Use secret key from environment or fallback
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret')

# Use absolute path to avoid file not found issues
EXCEL_FILE = os.path.join(os.getcwd(), 'ecommerce_data.xlsx')

# Initialize Excel file
def initialize_excel():
    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            pd.DataFrame(columns=['id', 'name', 'price', 'image']).to_excel(writer, sheet_name='Products', index=False)
            pd.DataFrame(columns=['username', 'password']).to_excel(writer, sheet_name='Users', index=False)
            pd.DataFrame(columns=['username', 'items', 'total']).to_excel(writer, sheet_name='Orders', index=False)

def read_all_products():
    df = pd.read_excel(EXCEL_FILE, sheet_name='Products')
    return df.to_dict(orient='records')

def read_users():
    df = pd.read_excel(EXCEL_FILE, sheet_name='Users')
    return df.to_dict(orient='records')

def save_user(username, password):
    df = pd.read_excel(EXCEL_FILE, sheet_name='Users')
    df = pd.concat([df, pd.DataFrame([{'username': username, 'password': password}])], ignore_index=True)
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='Users', index=False)

def get_product_by_id(product_id):
    df = pd.read_excel(EXCEL_FILE, sheet_name='Products')
    product = df[df['id'] == product_id]
    return product.iloc[0].to_dict() if not product.empty else None

def save_order(username, items, total):
    df = pd.read_excel(EXCEL_FILE, sheet_name='Orders')
    new_order = pd.DataFrame([{'username': username, 'items': str(items), 'total': total}])
    df = pd.concat([df, new_order], ignore_index=True)
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='Orders', index=False)

@app.route('/')
def index():
    search = request.args.get('search')
    products = read_all_products()
    if search:
        products = [p for p in products if search.lower() in p['name'].lower()]
    return render_template('index.html', products=products)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = read_users()
        if any(user['username'] == username for user in users):
            return 'Username already exists. Please choose another one.'
        save_user(username, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = read_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['cart'] = []
                return redirect(url_for('index'))
        return 'Invalid username or password.'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    product = get_product_by_id(product_id)
    if product:
        session['cart'].append(product)
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/checkout')
def checkout():
    if 'username' in session:
        username = session['username']
        cart_items = session.get('cart', [])
        total = sum(item['price'] for item in cart_items)
        save_order(username, cart_items, total)
        session['cart'] = []
        return render_template('checkout.html', total=total)
    return redirect(url_for('login'))

@app.route('/track')
def track():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    df = pd.read_excel(EXCEL_FILE, sheet_name='Orders')
    user_orders = df[df['username'] == username].to_dict(orient='records')
    return render_template('track.html', orders=user_orders)

# ✅ DEPLOYMENT START
if __name__ == '__main__':
    initialize_excel()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
