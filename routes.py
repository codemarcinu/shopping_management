from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from db import get_db_connection, initialize_db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            name = request.form['name']
            category = request.form['category']
            purchase_date = request.form['purchase_date']
            expiry_date = request.form.get('expiry_date')
            quantity = request.form['quantity']
            price = request.form['price']
            location = request.form['location']
            status = request.form.get('status', 'available')

            if not name or category not in current_app.config['CATEGORIES']:
                flash('Invalid product data.', 'danger')
                return redirect(url_for('main.add_product'))
            if location not in current_app.config['LOCATIONS']:
                flash('Invalid location.', 'danger')
                return redirect(url_for('main.add_product'))
            try:
                quantity = int(quantity)
                price = float(price)
                if quantity <= 0 or price < 0:
                    raise ValueError()
            except ValueError:
                flash('Quantity and price must be valid numbers.', 'danger')
                return redirect(url_for('main.add_product'))
            try:
                datetime.strptime(purchase_date, '%Y-%m-%d')
                if expiry_date:
                    datetime.strptime(expiry_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format.', 'danger')
                return redirect(url_for('main.add_product'))

            with get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO products (name, category, purchase_date, expiry_date,
                    quantity, price, location, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, category, purchase_date, expiry_date, quantity, price, location, status))
                conn.commit()

            flash('Product added successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template(
        'add_product.html',
        categories=current_app.config['CATEGORIES'],
        locations=current_app.config['LOCATIONS'],
        statuses=current_app.config['STATUSES']
    )

@main.route('/inventory')
def list_products():
    sort_by = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')
    with get_db_connection() as conn:
        products = conn.execute(f'''
            SELECT * FROM products
            ORDER BY {sort_by} {order.upper()}
        ''').fetchall()
    return render_template('product_list.html', products=products)

@main.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('main.list_products'))

@main.route('/cook', methods=['GET', 'POST'])
def cook():
    if request.method == 'POST':
        used_products = request.form.getlist('products')
        with get_db_connection() as conn:
            for product_id in used_products:
                conn.execute('''
                    UPDATE products
                    SET status = 'unavailable', quantity = quantity - 1
                    WHERE id = ? AND quantity > 0
                ''', (product_id,))
            conn.commit()
        flash(f'{len(used_products)} products used.', 'success')
        return redirect(url_for('main.cook'))

    with get_db_connection() as conn:
        products = conn.execute('SELECT * FROM products WHERE quantity > 0').fetchall()
    return render_template('cooking.html', products=products)
