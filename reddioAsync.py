import logging
from web3 import AsyncWeb3
from typing import Optional
from clientAsync import AsyncClient
from config import DEPOSIT_ABI, WITHDRAW_ABI, CONTRACT_ADDRESS
from utils import read_json
from models import TokenAmount


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Reddio:
    deposit_abi = None
    withdraw_abi = None
    router_address = None

    def __init__(self, client: AsyncClient, wallet_address: str):
        self.client = client
        self.wallet_address = AsyncWeb3.to_checksum_address(wallet_address)

    @classmethod
    async def async_initialize(cls):
        cls.deposit_abi = await read_json(DEPOSIT_ABI)
        cls.withdraw_abi = await read_json(WITHDRAW_ABI)
        cls.router_address = AsyncWeb3.to_checksum_address(CONTRACT_ADDRESS)

    async def depositETH(self, amount: TokenAmount, escrow_fee: TokenAmount):
        try:
            contract = self.client.w3.eth.contract(
                abi=Reddio.deposit_abi,
                address=Reddio.router_address
            )

            data = contract.encode_abi(
                'depositETH',
                args=(
                    self.wallet_address,
                    amount.Wei,
                    escrow_fee.Wei
                )
            )

            return await self.client.send_transaction(
                to=Reddio.router_address,
                data=data,
                value=amount.Wei
            )
        except Exception as e:
            logging.error(f"Error in depositETH: {e}")
            return None

    async def withdraw_eth(self, amount):
        try:
            contract = self.client.w3.eth.contract(
                abi=Reddio.withdraw_abi,
                address=Reddio.router_address
            )

            data = contract.encode_abi(
                'withdrawETH',
                args=(
                    self.wallet_address,
                    amount,
                )
            )

            return await self.client.send_transaction(
                to=Reddio.router_address,
                data=data
            )
        except Exception as e:
            logging.error(f"Error in withdraw_eth: {e}")
            return None

    # Uncomment and use the following method if needed
    # async def withdraw_red(self):
    #     try:
    #         contract = self.client.w3.eth.contract(
    #             abi=Reddio.withdraw_abi,
    #             address=Reddio.router_address
    #         )

    #         data = contract.encode_abi(
    #             'withdrawRED',
    #             args=(
    #                 self.wallet_address
    #             )
    #         )

    #         return await self.client.send_transaction(
    #             to=Reddio.router_address,
    #             data=data
    #         )
    #     except Exception as e:
    #         logging.error(f"Error in withdraw_red: {e}")
    #         return None
