
import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = os.urandom(24)

    # Ścieżka do bazy danych
    DATABASE = os.path.join(BASE_DIR, 'zakupy.db')

    # Stałe aplikacji
    KATEGORIE = ['Nabiał', 'Pieczywo', 'Mięso', 'Warzywa', 'Owoce', 'Napoje', 'Przekąski']
    LOKALIZACJE = ['Lodówka', 'Zamrażarka', 'Spiżarnia', 'Szafka kuchenna']
    STATUSY = ['dostępny', 'kończący się', 'niedostępny']
