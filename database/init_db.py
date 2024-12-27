import sqlite3
import os

def initialize_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_address TEXT UNIQUE NOT NULL,
        private_key TEXT UNIQUE NOT NULL,
        is_register TEXT CHECK(is_register IN ('TRUE', 'FALSE')) DEFAULT 'FALSE',
        twitter_auth_token TEXT UNIQUE NOT NULL,
        user_agent TEXT NOT NULL
    );
    ''')


    conn.commit()
    conn.close()

    print(f"База данных создана по пути: {db_path}")
