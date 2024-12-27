import asyncio
import logging
import aiohttp
import random
import twitter
from reddioAsync import Reddio
from clientAsync import AsyncClient
from config import ETH_SEPOLIA_RPC, CLIENT_ID
from models import TokenAmount
from database.db_utils import add_account, delete_account, print_all_accounts, update_account
from database.db_utils import get_unregistered_wallets, get_registered_wallets, get_auth_token, get_private_key
from database.init_db import initialize_database


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_pre_register(wallet_address: str) -> str:
    url = "https://points-mainnet.reddio.com/v1/pre_register"

    payload = {
        "wallet_address": wallet_address
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0 (Edition Yx GX)",
        "Referer": "https://points.reddio.com/",
        "Sec-CH-UA": '"Chromium";v="128", "Not;A=Brand";v="24", "Opera GX";v="114"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    #response_json = await response.json()
                    #logger.info("Response JSON: %s", response_json)
                    return "OK"
                else:
                    error_message = await response.json()
                    #logger.warning(f"Error: {response.status} - {error_message}")
                    return error_message.get("error", "Unknown error")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)} 
    

async def get_state(wallet_address: str) -> str:
    url = "https://points-mainnet.reddio.com/v1/login/twitter"

    payload = {
        "wallet_address": wallet_address
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0 (Edition Yx GX)",
        "Referer": "https://points.reddio.com/",
        "Sec-CH-UA": '"Chromium";v="128", "Not;A=Brand";v="24", "Opera GX";v="114"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    response_json = await response.json()
                    #logger.info("Response JSON: %s", response_json)
                    state = response_json.get("data", {}).get("url", "").split("state=")[-1].split("&")[0]
                    #logger.info("Extracted state: %s", state)
                    return state
                else:
                    error_message = await response.json()
                    logger.warning(f"Error: {response.status} - {error_message}")
                    return error_message.get("error", "Unknown error")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}


async def auth_twitter(auth_token: str, state: str):
    twitter_account = twitter.Account(auth_token=auth_token)
    async with twitter.Client(
        twitter_account, 
        proxy="http://user132834:gyckq8@45.159.180.72:3840",
        auto_relogin=True,
        update_account_info_on_startup=True,
        verify=False, 
        trust_env=True
    ) as twitter_client:
        print(f"Logged in as @{twitter_account.username} (id={twitter_account.id})")

        oauth2_data = {
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'redirect_uri': 'https://points-mainnet.reddio.com/v1/auth/twitter/callback',
            'scope': 'tweet.read like.read users.read follows.read follows.write offline.access',
            'state': state,
            'code_challenge': 'challenge',
            'code_challenge_method': 'plain'
        }

        auth_code = await twitter_client.oauth2(**oauth2_data)

        url = "https://points-mainnet.reddio.com/v1/auth/twitter/callback"
        params = {
            'state': state,
            'code': auth_code
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36',
            'Referer': 'https://twitter.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ru,en;q=0.9'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                status_code = response.status
                headers = response.headers
                response_text = await response.text()

        print(f"Request status: {status_code}")


async def doTrans(wallet_address: str, private_key: str):
    client = AsyncClient(private_key=private_key, rpc=ETH_SEPOLIA_RPC)
    reddio = Reddio(client=client, wallet_address=wallet_address)

    await client.async_initialize()
    await reddio.async_initialize()

    balance = await client.get_balance()
    percentage = random.uniform(1, 3) / 100
    amount = balance * percentage
    fee = amount/20

    print(amount)
    print(fee)


    amount = TokenAmount(amount=amount)  
    escrow_fee = TokenAmount(amount=fee)

    try:
        logger.info("Starting depositETH transaction...")
        tx = await reddio.depositETH(amount=amount, escrow_fee=escrow_fee)
    except Exception as e:
        logger.error(f"Error during deposit: {e}", exc_info=True)
        return 

    try:
        logger.info("Verifying transaction...")
        res = await reddio.client.verif_tx(tx_hash=tx)
        logger.info(f"Transaction verification result: {res}")
    except Exception as e:
        logger.error(f"Unexpected error in verif_tx function: {e}", exc_info=True)


async def claim_red(wallet_address: str):
    url = "https://testnet-faucet.reddio.com/api/claim/new"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://testnet-faucet.reddio.com",
        "referer": "https://testnet-faucet.reddio.com/",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Opera GX";v="114"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0 (Edition Yx GX)",
        "cookie": "_ga=GA1.1.881854413.1734472555; _ga_15513WPM38=GS1.1.1734606432.12.1.1734606913.0.0.0"
    }

    payload = {
        "address": wallet_address,
        "others": False
    }

    try:
        logger.info("Starting RED claim request...")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=200) as response:
                logger.info(f"Status Code: {response.status}")
                
                if response.status == 200:
                    response_data = await response.json()
                    logger.info(f"Response Body: {response_data}")
                else:
                    logger.warning(f"Failed to claim RED: Status Code {response.status}")
    except Exception as e:
        logger.error(f"Error during RED claim: {e}", exc_info=True)

async def main():
    MENU = (
        f"1 - init db\n"
        f"2 - add account\n"
        f"3 - print all accounts\n"
        f"4 - delete account\n"
        f"5 - do transaction\n"
        f"6 - claim RED\n"
        f"7 - register users \n"
        f"8 - change account info\n"
        f"9 - do claim and tx\n"
        f"10 - auth twitter for registred\n"
        f"0 - exit\n"
    )

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        match choice:
            case "1":
                initialize_database()
            case "2":
                wallet_address = input("Enter wallet address: ").strip()
                private_key = input("Enter private key : ").strip()
                auth_token = input("Enter auth token: ").strip()
                await add_account(wallet_address=wallet_address, private_key=private_key, is_register="FALSE", twitter_auth_token=auth_token)
            case "3":
                await print_all_accounts()
            case "4":
                wallet_address = input("Enter wallet address: ").strip()
                await delete_account(wallet_address=wallet_address)
            case "5":
                await doTrans()
            case "6":
                wallet_address = input("Enter wallet address to claim RED: ").strip()
                await claim_red(wallet_address)
            case "7":
                unregistered_wallets = await get_unregistered_wallets()

                if not unregistered_wallets:
                    print("No unregistered accounts found.\n")
                else:
                    for wallet_address in unregistered_wallets:
                        res = await send_pre_register(wallet_address)
                        if res == "User already pre registered" or res == "OK":
                            await update_account(wallet_address=wallet_address, field="is_register", new_value="TRUE")
                            print(f"for wallet: {wallet_address}, error: {res}, is_register was updated\n")
                        else:
                            print(f"for wallet: {wallet_address}, error: {res}\n")
            case "8":
                wallet_address = input("Enter wallet address: ").strip()
                field = input("Enter field : ").strip()
                new_value = input("Enter new_value: ").strip()
                await update_account(wallet_address=wallet_address, field=field, new_value=new_value)
                print(f"wallet {wallet_address} was updated\n")
            case "9":
                registered_wallets = await get_registered_wallets()

                if registered_wallets:
                    for wallet_address in registered_wallets:
                        await claim_red(wallet_address)
                        private_key = await get_private_key(wallet_address)
                        await doTrans(wallet_address=wallet_address, private_key=private_key)

            case "10":
                registered_wallets = await get_registered_wallets()

                if registered_wallets:
                    for wallet_address in registered_wallets:
                        state = await get_state(wallet_address)
                        auth_token = await get_auth_token(wallet_address)
                        await auth_twitter(auth_token=auth_token, state=state)
            case "0":
                logger.info("Exiting the program.")
                break
            case _:
                logger.warning("Invalid choice, please try again.")


if __name__ == "__main__":
    asyncio.run(main())
