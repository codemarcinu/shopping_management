from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from db import get_db_connection
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dodaj', methods=['GET', 'POST'])
def dodaj_produkt():
    if request.method == 'POST':
        try:
            nazwa = request.form['nazwa']
            sklep = request.form['sklep']
            kategoria = request.form['kategoria']
            data_zakupu = request.form['data_zakupu']
            data_waznosci = request.form.get('data_waznosci')
            ilosc = request.form['ilosc']
            cena = request.form['cena']
            lokalizacja = request.form['lokalizacja']
            status = request.form.get('status', 'available')

            if not nazwa or not sklep or kategoria not in current_app.config['CATEGORIES']:
                flash('Nieprawidłowe dane produktu.', 'danger')
                return redirect(url_for('main.dodaj_produkt'))
            if lokalizacja not in current_app.config['LOCATIONS']:
                flash('Nieprawidłowa lokalizacja.', 'danger')
                return redirect(url_for('main.dodaj_produkt'))

            try:
                ilosc = int(ilosc)
                cena = float(cena)
                if ilosc <= 0 or cena < 0:
                    raise ValueError()
            except ValueError:
                flash('Ilość i cena muszą być poprawnymi liczbami.', 'danger')
                return redirect(url_for('main.dodaj_produkt'))
            try:
                datetime.strptime(data_zakupu, '%Y-%m-%d')
                if data_waznosci:
                    datetime.strptime(data_waznosci, '%Y-%m-%d')
            except ValueError:
                flash('Nieprawidłowy format daty.', 'danger')
                return redirect(url_for('main.dodaj_produkt'))

            with get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO products (name, store, category, purchase_date, expiry_date,
                    quantity, price, location, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nazwa, sklep, kategoria, data_zakupu, data_waznosci, ilosc, cena, lokalizacja, status))
                conn.commit()

            flash('Produkt dodany pomyślnie!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'Wystąpił błąd: {str(e)}', 'danger')
    return render_template(
        'add_product.html',
        categories=current_app.config['CATEGORIES'],
        locations=current_app.config['LOCATIONS'],
        statuses=current_app.config['STATUSES']
    )

@main.route('/produkty')
def lista_produktow():
    sortuj_po = request.args.get('sortuj_po', 'name')
    kolejnosc = request.args.get('kolejnosc', 'asc')

    kategoria = request.args.get('kategoria')
    status = request.args.get('status')
    lokalizacja = request.args.get('lokalizacja')

    kolumny_sortowania = ['name', 'purchase_date', 'expiry_date', 'quantity']
    if sortuj_po not in kolumny_sortowania:
        sortuj_po = 'name'

    kolejnosc_sql = 'ASC' if kolejnosc == 'asc' else 'DESC'

    query = 'SELECT * FROM products WHERE 1=1'
    params = []

    # Dodajemy filtry, jeśli są podane
    if kategoria:
        query += ' AND category = ?'
        params.append(kategoria)
    if status:
        query += ' AND status = ?'
        params.append(status)
    if lokalizacja:
        query += ' AND location = ?'
        params.append(lokalizacja)

    query += f' ORDER BY {sortuj_po} {kolejnosc_sql}'

    with get_db_connection() as conn:
        produkty = conn.execute(query, params).fetchall()

    return render_template(
        'product_list.html',
        produkty=produkty,
        sortuj_po=sortuj_po,
        kolejnosc=kolejnosc,
        categories=current_app.config['CATEGORIES'],
        locations=current_app.config['LOCATIONS']
    )

@main.route('/co-mam')
def co_mam():
    with get_db_connection() as conn:
        produkty = conn.execute('SELECT * FROM products WHERE quantity > 0').fetchall()
    return render_template('product_list.html', produkty=produkty)

@main.route('/usun/<int:id>', methods=['POST'])
def usun_produkt(id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
    flash('Produkt usunięty.', 'success')
    return redirect(url_for('main.lista_produktow'))

@main.route('/gotuje', methods=['GET', 'POST'])
def gotuje():
    if request.method == 'POST':
        zuzyte_produkty = request.form.getlist('produkty')
        with get_db_connection() as conn:
            for produkt_id in zuzyte_produkty:
                conn.execute('''
                    UPDATE products
                    SET status = 'unavailable', quantity = quantity - 1
                    WHERE id = ? AND quantity > 0
                ''', (produkt_id,))
            conn.commit()
        flash(f'Zużyto {len(zuzyte_produkty)} produkty.', 'success')
        return redirect(url_for('main.gotuje'))

    with get_db_connection() as conn:
        produkty = conn.execute('SELECT * FROM products WHERE quantity > 0').fetchall()
    return render_template('cooking.html', produkty=produkty)
