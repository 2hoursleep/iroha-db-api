from .block_collector import IrohaBlockClient
from .models import Block_V1
from .cronjob import huey
from . import _print
import os
import json
from rich.progress import Progress


class IrohaBlockAPI:
    def __init__(self, api_user, private_key, iroha_host) -> None:
        self.private_key = private_key
        self.api_user = api_user
        self.iroha_host = iroha_host
        self.iroha_block_api = IrohaBlockClient(
            creator_account=api_user,
            private_key=private_key,
            iroha_host=iroha_host,
        )

    @huey.task()
    def parse_iroha_blocks_to_db(self, height: int = 2) -> None:
        """
        Iroha Block Parser
        :param height: Address of the Sender,
        :param return_block: Returns block in JSON Format
        :return: None if return_block is false
        """
        try:
            block = json.loads(self.iroha_block_api.get_blocks(height=height))
            height = block["blockResponse"]["block"]["blockV1"]["payload"]["height"]
            prev_block_hash = block["blockResponse"]["block"]["blockV1"]["payload"][
                "prevBlockHash"
            ]
            created_time = block["blockResponse"]["block"]["blockV1"]["payload"][
                "createdTime"
            ]
            signatures = block["blockResponse"]["block"]["blockV1"]["signatures"]
            try:
                rejected_transactions_hashes = block["blockResponse"]["block"][
                    "blockV1"
                ]["payload"]["rejectedTransactionsHashes"]
            except:
                rejected_transactions_hashes = []
            try:
                transactions = block["blockResponse"]["block"]["blockV1"]["payload"][
                    "transactions"
                ]
            except:
                transactions = []
            Block_V1.add_block(
                created_time=created_time,
                height=height,
                prev_block_hash=prev_block_hash,
                transactions=transactions,
                rejected_transactions_hashes=rejected_transactions_hashes,
                signatures=signatures,
            )
        except Exception as error:
            _print(error)

    def parse_genesis_iroha_block_to_db(self) -> None:
        """"""
        try:
            raw_block = self.iroha_block_api.get_blocks(height=1)
            block = json.loads(raw_block)
            transactions = block["blockResponse"]["block"]["blockV1"]["payload"][
                "transactions"
            ]
            prev_block_hash = block["blockResponse"]["block"]["blockV1"]["payload"][
                "prevBlockHash"
            ]
            height = block["blockResponse"]["block"]["blockV1"]["payload"]["height"]
            txNumber = block["blockResponse"]["block"]["blockV1"]["payload"]["txNumber"]
            Block_V1.add_block(
                created_time="0",
                height=height,
                prev_block_hash=prev_block_hash,
                transactions=transactions,
                rejected_transactions_hashes=[],
                signatures=[],
            )
        except:
            _print(
                "[bold red]Genesis Block already exists or cannot connect to Iroha[/bold red]"
            )

    def run_block_paser(self, scan_range: int = 100):
        # get last block from db if none start from 1
        try:
            huey.start()
            last_block = Block_V1.get_last_block()
            last_height = last_block["height"]
            if last_height:
                self.block_parser(last_height, scan_range)
        except:
            _print(f"[bold red]Unable to get block from db[/bold red]")
            raise
        finally:
            huey.stop()

    def block_parser(self, last_height: int, scan_range: int = 100):
        curent_height = last_height + 1
        end_height = curent_height + scan_range
        while self.test_block_height(curent_height):
            self.parse_iroha_blocks_to_db(height=curent_height)
            curent_height += 1
        else:
            _print(f"[bold green]Finished parsing\nLast Block no: {curent_height}[/bold green]")

    def test_block_height(self, height: int = 2):
        """
        Tests if Iroha block exists
        :param height: Height as integer,
        :return: Boolean True if height matches
        """
        try:
            block = json.loads(self.iroha_block_api.get_blocks(height=height))
            block_height = int(
                block["blockResponse"]["block"]["blockV1"]["payload"]["height"]
            )
            assert block_height == height
            return True
        except:
            return False
