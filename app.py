
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicjalizacja bazy danych
    from db import initialize_db, close_db
    with app.app_context():
        initialize_db()
    app.teardown_appcontext(close_db)

    # Rejestracja routingów
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
