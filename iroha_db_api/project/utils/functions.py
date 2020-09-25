# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import json
import os

from project.server.models import Block_V1, Wsv_Block_Info
from rich.progress import Progress

from . import _print
from .block_collector import IrohaBlockClient
from .cronjob import huey


class IrohaBlockAPI:
    """
    Iroha Block Client API.
    Connects to Iroha V1 Node using getBlocks command.
    Parses block data to Database Table.
    Note: Currently only Postgres is supported
    :params:
    type: String :api_user: API User account used as Iroha Creator Account
    type: String :private_key: API Account private key
    type: String :iroha_host: Iroha node host address (ip+port or dns)
    e.g. localhost:50051
    """

    def __init__(self, api_user, private_key, iroha_host) -> None:
        self.private_key = private_key
        self.api_user = api_user
        self.iroha_host = iroha_host
        self.iroha_block_api = IrohaBlockClient(
            creator_account=api_user, private_key=private_key, iroha_host=iroha_host
        )

    @huey.task()
    def parse_iroha_blocks_to_db(self, height: int = 2) -> None:
        """
        Iroha Block Parser
        :params:
        type: Integer :height: Height as integer
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
        """Parses Block Height No: 1 from Iroha to DB"""
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

    def block_parser(self, last_height: int, scan_range: int = 100):
        curent_height = last_height + 1
        end_height = curent_height + scan_range
        while self.test_block_height(curent_height):
            self.parse_iroha_blocks_to_db(height=curent_height)
            curent_height += 1
        else:
            _print(
                f"[bold green]Finished parsing\nLast Block no: {curent_height}[/bold green]"
            )

    def test_block_height(self, height: int = 2):
        """
        Tests if Iroha block exists
        :params:
        type: Integer :height: Height as integer
        :return:
        type: Boolean
        True if height matches
        False if error occurs
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

    def get_wsv_height(self) -> int:
        """
        Query Iroha Wsv Top Block
        :returns: Int height
        """
        try:
            wsv_top_block = Wsv_Block_Info.query.first()
            assert wsv_top_block.height
            return wsv_top_block.height
        except Exception:
            _print(Exception)

    def cron_block_parser(self):
        """
        Runs cronjob worker to parse blocks
        from current DB height to Iroha wsv height.
        :params: None
        :return: None
        """
        _print(f"[bold yellow]Starting parser\n[/bold yellow]")
        # Get last block from db and load height field
        try:
            db_last_block = Block_V1.get_last_block()
            db_last_height = db_last_block["height"]
        except Exception as error:
            _print("No blocks found in db. \nAdding Genesis block")
            self.parse_genesis_iroha_block_to_db()
        finally:
            db_last_block = Block_V1.get_last_block()
            db_last_height = db_last_block["height"]
        # Get wsv info from Iroha
        wsv_height = self.get_wsv_height()
        # Increment no to start from new height
        height = db_last_height + 1
        while height < wsv_height:
            self.parse_blocks_cron_job(height)
            db_last_block = Block_V1.get_last_block()
            db_last_height = db_last_block["height"]
            assert db_last_height == height
            height += 1
        else:
            db_last_block = Block_V1.get_last_block()
            db_last_height = db_last_block["height"]
            _print(
                f"[bold green]Finished parsing\nLast Block no:[/bold green] [bold red]{db_last_height}[/bold red]"
            )

    def parse_blocks_cron_job(self, height: int) -> None:
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
            except Exception as error:
                rejected_transactions_hashes = []
            try:
                transactions = block["blockResponse"]["block"]["blockV1"]["payload"][
                    "transactions"
                ]
            except Exception as error:
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
