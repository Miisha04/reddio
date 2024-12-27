import aiosqlite
import os
import logging



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'database.db')

async def add_account(wallet_address, private_key, is_register, twitter_auth_token, user_agent):
    async with aiosqlite.connect(db_path) as conn:
        try:
            await conn.execute('''
            INSERT INTO accounts (wallet_address, private_key, is_register, twitter_auth_token, user_agent)
            VALUES (?, ?, ?, ?, ?)
            ''', (wallet_address, private_key, is_register, twitter_auth_token, user_agent))
            await conn.commit()
            logging.info("Account added successfully!")
        except aiosqlite.Error as e:
            logging.error(f"Error adding account: {e}")

async def delete_account(wallet_address):
    async with aiosqlite.connect(db_path) as conn:
        try:
            await conn.execute('''
            DELETE FROM accounts WHERE wallet_address = ?
            ''', (wallet_address,))
            await conn.commit()
            logging.info("Account deleted successfully!")
        except aiosqlite.Error as e:
            logging.error(f"Error deleting account: {e}")

async def update_account(wallet_address, field, new_value):
    async with aiosqlite.connect(db_path) as conn:
        try:
            await conn.execute(f'''
            UPDATE accounts SET {field} = ? WHERE wallet_address = ?
            ''', (new_value, wallet_address))
            await conn.commit()
            logging.info(f"Account updated successfully: {wallet_address}, {field} = {new_value}")
        except aiosqlite.Error as e:
            logging.error(f"Error updating account: {e}")

async def print_all_accounts():
    async with aiosqlite.connect(db_path) as conn:
        try:
            async with conn.execute('SELECT * FROM accounts') as cursor:
                accounts = await cursor.fetchall()
                if accounts:
                    for account in accounts:
                        logging.info(account)
                else:
                    logging.info("No accounts found.")
        except aiosqlite.Error as e:
            logging.error(f"Error fetching accounts: {e}")

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
            logging.error(f"Error fetching unregistered wallets: {e}")
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
            logging.error(f"Error fetching registered wallets: {e}")
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
                    logging.warning(f"Cannot get token for {wallet_address}")
                    return ""
        except aiosqlite.Error as e:
            logging.error(f"Error fetching auth token: {e}")
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
                    logging.warning(f"Cannot get key for {wallet_address}")
                    return ""
        except aiosqlite.Error as e:
            logging.error(f"Error fetching private key: {e}")
            return ""


async def get_user_agent(wallet_address: str) -> str:
    async with aiosqlite.connect(db_path) as conn:
        try:
            async with conn.execute('''
            SELECT user_agent FROM accounts WHERE wallet_address = ?
            ''', (wallet_address,)) as cursor:
                result = await cursor.fetchone()

                if result:
                    return result[0]
                else:
                    logging.warning(f"Cannot get user_agent for {wallet_address}")
                    return ""
        except aiosqlite.Error as e:
            logging.error(f"Error fetching user_agent: {e}")
            return ""
