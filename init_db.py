from app import create_app
from db import initialize_db

app = create_app()

with app.app_context():
    initialize_db()
    print("Baza danych została zainicjalizowana.")

