from flask import Flask
from routes import main
from db import initialize_db, close_db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')  # Ładowanie konfiguracji bezpośrednio z pliku config.py

    # Inicjalizacja bazy danych
    with app.app_context():
        initialize_db()

    # Rejestracja blueprintów
    app.register_blueprint(main)

    # Obsługa zamykania połączenia z bazą danych
    app.teardown_appcontext(close_db)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
