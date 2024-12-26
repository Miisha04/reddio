import asyncio
import logging
from typing import Optional
from web3 import AsyncWeb3, AsyncHTTPProvider
from aiohttp import ClientSession

from models import DefaultABIs, TokenAmount
from utils import read_json
from config import TOKEN_ABI


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncClient:
    default_abi = None  

    def __init__(self, private_key: str, rpc: str):
        self.private_key = private_key
        self.rpc = rpc
        self.w3 = AsyncWeb3(AsyncHTTPProvider(endpoint_uri=self.rpc))
        self.address = AsyncWeb3.to_checksum_address(self.w3.eth.account.from_key(private_key=private_key).address)

    @classmethod
    async def async_initialize(cls):
        cls.default_abi = await read_json(TOKEN_ABI)


    async def get_decimals(self, contract_address: str) -> int:
        try:
            contract = self.w3.eth.contract(
                address=AsyncWeb3.to_checksum_address(contract_address),
                abi=self.default_abi
            )
            decimals = await contract.functions.decimals().call()
            logger.info(f"Decimals for {contract_address}: {decimals}")
            return decimals
        except Exception as e:
            logger.error(f"Error in get_decimals: {e}")
            return 0

    async def balance_of(self, contract_address: str, address: Optional[str] = None):
        try:
            if not address:
                address = self.address
            contract = self.w3.eth.contract(
                address=AsyncWeb3.to_checksum_address(contract_address),
                abi=self.default_abi
            )
            balance = await contract.functions.balanceOf(address).call()
            logger.info(f"Balance for {address} on {contract_address}: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Error in balance_of: {e}")
            return 0

    async def get_allowance(self, token_address: str, spender: str):
        try:
            contract = self.w3.eth.contract(
                address=AsyncWeb3.to_checksum_address(token_address),
                abi=self.default_abi
            )
            allowance = await contract.functions.allowance(self.address, spender).call()
            logger.info(f"Allowance for {spender} on {token_address}: {allowance}")
            return allowance
        except Exception as e:
            logger.error(f"Error in get_allowance: {e}")
            return 0

    async def check_balance_interface(self, token_address: str, min_value: float) -> bool:
        try:
            logger.info(f"Checking balance for {token_address} with min value {min_value}")
            balance = await self.balance_of(contract_address=token_address)
            decimal = await self.get_decimals(contract_address=token_address)
            if balance < min_value * 10 ** decimal:
                logger.warning(f"Not enough balance for {token_address}. Required: {min_value}, Available: {balance / 10 ** decimal}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error in check_balance_interface: {e}")
            return False

    async def send_transaction(self, to, data=None, from_=None, increase_gas=1.1, value=None):
        try:
            if not from_:
                from_ = self.address

            tx_params = {
                'chainId': await self.w3.eth.chain_id,
                'nonce': await self.w3.eth.get_transaction_count(self.address),
                'from': AsyncWeb3.to_checksum_address(from_),
                'to': AsyncWeb3.to_checksum_address(to),
                'gasPrice': await self.w3.eth.gas_price
            }
            if data:
                tx_params['data'] = data
            if value:
                tx_params['value'] = value
            tx_params['gas'] = int(400000 * increase_gas)

            sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(sign.raw_transaction)
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            return tx_hash
        except Exception as e:
            logger.error(f"Error in send_transaction: {e}")
            return None

    async def verif_tx(self, tx_hash) -> bool:
        try:
            data = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
            if 'status' in data and data['status'] == 1:
                logger.info(f"Transaction successful: {tx_hash.hex()}")
                return True
            else:
                logger.warning(f"Transaction failed: {data.get('transactionHash', tx_hash).hex()}")
                return False
        except Exception as e:
            logger.error(f"Error in verif_tx: {e}")
            return False

    async def get_eth_price(self, token='ETH'):
        try:
            token = token.upper()
            logger.info(f"Getting price for {token}")
            url = f'https://api.binance.com/api/v3/depth?limit=1&symbol={token}USDT'
            async with ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Error in get_eth_price: code {response.status}, response: {await response.json()}")
                        return None
                    result_dict = await response.json()
                    if 'asks' not in result_dict:
                        logger.error(f"Invalid response in get_eth_price: {result_dict}")
                        return None
                    price = float(result_dict['asks'][0][0])
                    logger.info(f"Price for {token}: {price}")
                    return price
        except Exception as e:
            logger.error(f"Error in get_eth_price: {e}")
            return None
        

    async def get_balance(self):
        balance = await self.w3.eth.get_balance(self.address) / 10**18

        return balance

        
        
