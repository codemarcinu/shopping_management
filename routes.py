from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from db import get_db_connection, get_expiring_products

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Strona główna
    return render_template('index.html')

@main.route('/dodaj', methods=['GET', 'POST'])
def dodaj_produkt():
    # Formularz dodawania nowego produktu
    if request.method == 'POST':
        try:
            nazwa = request.form['nazwa']
            kategoria = request.form['kategoria']
            data_zakupu = request.form['data_zakupu']
            data_waznosci = request.form['data_waznosci']
            ilosc = int(request.form['ilosc'])
            cena = float(request.form['cena'])
            lokalizacja = request.form['lokalizacja']
            status = request.form['status']

            with get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO produkty (nazwa, kategoria, data_zakupu, data_waznosci,
                    ilosc, cena, lokalizacja, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nazwa, kategoria, data_zakupu, data_waznosci, ilosc, cena, lokalizacja, status))
                conn.commit()

            flash('Produkt został dodany pomyślnie!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'Wystąpił błąd podczas dodawania produktu: {str(e)}', 'danger')

    return render_template(
        'add_product.html',
        kategorie=current_app.config['KATEGORIE'],
        lokalizacje=current_app.config['LOKALIZACJE'],
        statusy=current_app.config['STATUSY']
    )

@main.route('/co-mam')
def co_mam():
    # Pobieranie produktów z bazy danych
    with get_db_connection() as conn:
        produkty = conn.execute('SELECT * FROM produkty').fetchall()
    return render_template('product_list.html', produkty=produkty)

@main.route('/usun/<int:id>', methods=['POST'])
def usun_produkt(id):
    # Usunięcie produktu z bazy danych
    with get_db_connection() as conn:
        conn.execute('DELETE FROM produkty WHERE id = ?', (id,))
        conn.commit()
    flash('Produkt został usunięty.', 'success')
    return redirect(url_for('main.co_mam'))

@main.route('/gotuje', methods=['GET', 'POST'])
def gotuje():
    # Zaznaczanie produktów do zużycia
    if request.method == 'POST':
        zuzyte_produkty = request.form.getlist('produkty')
        with get_db_connection() as conn:
            for produkt_id in zuzyte_produkty:
                conn.execute('''
                    UPDATE produkty
                    SET status = 'niedostępny', ilosc = ilosc - 1
                    WHERE id = ? AND ilosc > 0
                ''', (produkt_id,))
            conn.commit()
        flash(f'Zużyto {len(zuzyte_produkty)} produkty.', 'success')
        return redirect(url_for('main.gotuje'))

    # Pobieranie dostępnych produktów
    with get_db_connection() as conn:
        produkty = conn.execute('SELECT * FROM produkty WHERE ilosc > 0').fetchall()
    return render_template('cooking.html', produkty=produkty)

