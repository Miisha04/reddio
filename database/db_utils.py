import sqlite3
import os

# Получаем абсолютный путь к базе данных
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'database.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_account(wallet_address, private_key, is_register, twitter_auth_token):
    try:
        cursor.execute('''
        INSERT INTO accounts (wallet_address, private_key, is_register, twitter_auth_token)
        VALUES (?, ?, ?, ?)
        ''', (wallet_address, private_key, is_register, twitter_auth_token))
        conn.commit()
        print("Account added successfully!\n")
    except sqlite3.Error as e:
        print(f"Error: {e}\n")

def delete_account(wallet_address):
    try:
        cursor.execute('''
        DELETE FROM accounts WHERE wallet_address = ?
        ''', (wallet_address,))
        conn.commit()
        print("Account deleted successfully!\n")
    except sqlite3.Error as e:
        print(f"Error: {e}\n")

def update_account(wallet_address, field, new_value):
    try:
        cursor.execute(f'''
        UPDATE accounts SET {field} = ? WHERE wallet_address = ?
        ''', (new_value, wallet_address))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}\n")

def print_all_accounts():
    try:
        cursor.execute('SELECT * FROM accounts')
        accounts = cursor.fetchall()
        if accounts:
            for account in accounts:
                print(account)
        else:
            print("No accounts found.\n")
    except sqlite3.Error as e:
        print(f"Error: {e}\n")

def get_unregistered_wallets():
    try:
        cursor.execute('''
        SELECT wallet_address FROM accounts WHERE is_register = 'FALSE'
        ''')
        wallets = cursor.fetchall()
        wallet_set = {wallet[0] for wallet in wallets}
        return wallet_set
    except sqlite3.Error as e:
        print(f"Error: {e}\n")
        return set()  
    

def get_registered_wallets():
    try:
        cursor.execute('''
        SELECT wallet_address FROM accounts WHERE is_register = 'TRUE'
        ''')
        wallets = cursor.fetchall()
        wallet_set = {wallet[0] for wallet in wallets}
        return wallet_set
    except sqlite3.Error as e:
        print(f"Error: {e}\n")
        return set()  
    
def get_auth_token(wallet_address: str):
    try:
        cursor.execute('''SELECT twitter_auth_token FROM accounts WHERE wallet_address = ? AND is_register = 'TRUE' ''', (wallet_address,))
        result = cursor.fetchone()

        if result:
            return result[0]  
        else:
            print(f"No registered wallet found for {wallet_address}")
            return ""  
    except sqlite3.Error as e:
        print(f"Error: {e}\n")
        return "" 
    

def get_private_key(wallet_address: str):
    try:
        cursor.execute('''SELECT private_key FROM accounts WHERE wallet_address = ? AND is_register = 'TRUE' ''', (wallet_address,))
        result = cursor.fetchone()

        if result:
            return result[0]  
        else:
            print(f"No registered wallet found for {wallet_address}")
            return ""  
    except sqlite3.Error as e:
        print(f"Error: {e}\n")
        return "" 

def close_connection():
    cursor.close()
    conn.close()
