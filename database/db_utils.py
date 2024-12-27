import aiosqlite
import os



base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'database.db')

async def add_account(wallet_address, private_key, is_register, twitter_auth_token):
    async with aiosqlite.connect(db_path) as conn:
        try:
            await conn.execute('''
            INSERT INTO accounts (wallet_address, private_key, is_register, twitter_auth_token)
            VALUES (?, ?, ?, ?)
            ''', (wallet_address, private_key, is_register, twitter_auth_token))
            await conn.commit()
            print("Account added successfully!\n")
        except aiosqlite.Error as e:
            print(f"Error: {e}\n")

async def delete_account(wallet_address):
    async with aiosqlite.connect(db_path) as conn:
        try:
            await conn.execute('''
            DELETE FROM accounts WHERE wallet_address = ?
            ''', (wallet_address,))
            await conn.commit()
            print("Account deleted successfully!\n")
        except aiosqlite.Error as e:
            print(f"Error: {e}\n")

async def update_account(wallet_address, field, new_value):
    async with aiosqlite.connect(db_path) as conn:
        try:
            await conn.execute(f'''
            UPDATE accounts SET {field} = ? WHERE wallet_address = ?
            ''', (new_value, wallet_address))
            await conn.commit()
        except aiosqlite.Error as e:
            print(f"Error: {e}\n")

async def print_all_accounts():
    async with aiosqlite.connect(db_path) as conn:
        try:
            async with conn.execute('SELECT * FROM accounts') as cursor:
                accounts = await cursor.fetchall()
                if accounts:
                    for account in accounts:
                        print(account)
                else:
                    print("No accounts found.\n")
        except aiosqlite.Error as e:
            print(f"Error: {e}\n")

async def get_unregistered_wallets() -> set:
    async with aiosqlite.connect(db_path) as conn:
        try:
            async with conn.execute('''
            SELECT wallet_address FROM accounts WHERE is_register = 'FALSE'
            ''') as cursor:
                wallets = await cursor.fetchall()
                wallet_set = {wallet[0] for wallet in wallets}
                return wallet_set
        except aiosqlite.Error as e:
            print(f"Error: {e}\n")
            return set()

async def get_registered_wallets() -> set:
    async with aiosqlite.connect(db_path) as conn:
        try:
            async with conn.execute('''
            SELECT wallet_address FROM accounts WHERE is_register = 'TRUE'
            ''') as cursor:
                wallets = await cursor.fetchall()
                wallet_set = {wallet[0] for wallet in wallets}
                return wallet_set
        except aiosqlite.Error as e:
            print(f"Error: {e}\n")
            return set()

async def get_auth_token(wallet_address: str) -> str:
    async with aiosqlite.connect(db_path) as conn:
        try:
            async with conn.execute('''
            SELECT twitter_auth_token FROM accounts WHERE wallet_address = ? AND is_register = 'TRUE'
            ''', (wallet_address,)) as cursor:
                result = await cursor.fetchone()

                if result:
                    return result[0]
                else:
                    print(f"No registered wallet found for {wallet_address}")
                    return ""
        except aiosqlite.Error as e:
            print(f"Error: {e}\n")
            return ""

async def get_private_key(wallet_address: str) -> str:
    async with aiosqlite.connect(db_path) as conn:
        try:
            async with conn.execute('''
            SELECT private_key FROM accounts WHERE wallet_address = ? AND is_register = 'TRUE'
            ''', (wallet_address,)) as cursor:
                result = await cursor.fetchone()

                if result:
                    return result[0]
                else:
                    print(f"No registered wallet found for {wallet_address}")
                    return ""
        except aiosqlite.Error as e:
            print(f"Error: {e}\n")
            return ""
