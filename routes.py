from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from db import get_db_connection

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Strona główna
    return render_template('index.html')

@main.route('/add', methods=['GET', 'POST'])
def add_product():
    # Formularz dodawania nowego produktu
    if request.method == 'POST':
        try:
            name = request.form['name']
            category = request.form['category']
            purchase_date = request.form['purchase_date']
            expiry_date = request.form['expiry_date']
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            location = request.form['location']
            status = request.form['status']

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
            flash(f'Error adding product: {str(e)}', 'danger')

    return render_template(
        'add_product.html',
        categories=current_app.config['CATEGORIES'],
        locations=current_app.config['LOCATIONS'],
        statuses=current_app.config['STATUSES']
    )

@main.route('/products')
def view_products():
    # Pobieranie produktów z bazy danych
    with get_db_connection() as conn:
        products = conn.execute('SELECT * FROM products').fetchall()
    return render_template('product_list.html', products=products)

@main.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    # Usunięcie produktu z bazy danych
    with get_db_connection() as conn:
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('main.view_products'))

@main.route('/cook', methods=['GET', 'POST'])
def cook_products():
    # Zaznaczanie produktów do zużycia
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
        return redirect(url_for('main.cook_products'))

    # Pobieranie dostępnych produktów
    with get_db_connection() as conn:
        products = conn.execute('SELECT * FROM products WHERE quantity > 0').fetchall()
    return render_template('cooking.html', products=products)
