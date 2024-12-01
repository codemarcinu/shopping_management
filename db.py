import sqlite3
from flask import current_app, g

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def initialize_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                store TEXT NOT NULL,
                category TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                expiry_date TEXT,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'available'
            )
        ''')
        conn.commit()
