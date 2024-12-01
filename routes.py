from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from db import get_db_connection
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
            store = request.form['store']
            category = request.form['category']
            purchase_date = request.form['purchase_date']
            expiry_date = request.form.get('expiry_date')
            quantity = request.form['quantity']
            price = request.form['price']
            location = request.form['location']
            status = request.form.get('status', 'available')

            if not name or not store or category not in current_app.config['CATEGORIES']:
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
                    INSERT INTO products (name, store, category, purchase_date, expiry_date,
                    quantity, price, location, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, store, category, purchase_date, expiry_date, quantity, price, location, status))
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

@main.route('/products')
def list_products():
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')

    category = request.args.get('category')
    status = request.args.get('status')
    location = request.args.get('location')

    sort_columns = ['name', 'purchase_date', 'expiry_date', 'quantity']
    if sort_by not in sort_columns:
        sort_by = 'name'

    order_sql = 'ASC' if order == 'asc' else 'DESC'

    query = 'SELECT * FROM products WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    if status:
        query += ' AND status = ?'
        params.append(status)
    if location:
        query += ' AND location = ?'
        params.append(location)

    query += f' ORDER BY {sort_by} {order_sql}'

    with get_db_connection() as conn:
        products = conn.execute(query, params).fetchall()

    return render_template(
        'product_list.html',
        products=products,
        sort_by=sort_by,
        order=order,
        categories=current_app.config['CATEGORIES'],
        locations=current_app.config['LOCATIONS']
    )

@main.route('/inventory')
def inventory():
    with get_db_connection() as conn:
        products = conn.execute('SELECT * FROM products WHERE quantity > 0').fetchall()
    return render_template('product_list.html', products=products)

@main.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
    flash('Product deleted.', 'success')
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
        flash(f'Used {len(used_products)} products.', 'success')
        return redirect(url_for('main.cook'))

    with get_db_connection() as conn:
        products = conn.execute('SELECT * FROM products WHERE quantity > 0').fetchall()
    return render_template('cooking.html', products=products)
