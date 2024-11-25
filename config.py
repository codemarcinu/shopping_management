import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = os.urandom(24)

    # Database path
    DATABASE = os.path.join(BASE_DIR, 'shopping.db')

    # Application constants
    CATEGORIES = ['Dairy', 'Bread', 'Meat', 'Vegetables', 'Fruits', 'Drinks', 'Snacks']
    LOCATIONS = ['Fridge', 'Freezer', 'Pantry', 'Kitchen Cabinet']
    STATUSES = ['available', 'running low', 'unavailable']
