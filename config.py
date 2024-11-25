import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.urandom(24)

DATABASE = os.path.join(BASE_DIR, 'shopping.db')

CATEGORIES = ['Nabiał', 'Pieczywo', 'Mięso', 'Warzywa', 'Owoce', 'Napoje', 'Przekąski']
LOCATIONS = ['Lodówka', 'Zamrażarka', 'Spiżarnia', 'Szafka kuchenna']
STATUSES = ['available', 'running low', 'unavailable']
