from sqlalchemy import Column, String, Integer, DateTime
import datetime
from .db import db, session, base
from sqlalchemy.dialects.postgresql.json import JSONB
from dataclasses import dataclass
from . import _print, click
import sys
from ._docker import start_postgres_docker
import time


@dataclass
class Block_V1(base):
    __tablename__ = "iroha_blocks"

    prev_block_hash = Column(String)
    height = Column(Integer, primary_key=True)
    added_on = Column(DateTime)
    created_time = Column(String)
    signatures = Column(JSONB)
    rejected_transactions_hashes = Column(JSONB)
    transactions = Column(JSONB)

    def __init__(
        self,
        prev_block_hash: str,
        created_time: str,
        height: int,
        transactions: JSONB,
        rejected_transactions_hashes: JSONB,
        signatures: JSONB,
    ) -> dict:
        self.prev_block_hash = prev_block_hash
        self.height = height
        self.created_time = created_time
        self.transactions = transactions
        self.rejected_transactions_hashes = rejected_transactions_hashes
        self.signatures = signatures
        self.added_on = datetime.datetime.now()

    def __repr__(self):
        return f"<id: Block Hash: {self.prev_block_hash} added \nHeight {self.height}"

    @staticmethod
    def add_block(
        prev_block_hash,
        created_time,
        height,
        transactions,
        rejected_transactions_hashes,
        signatures,
    ):
        # add Iroha block to database
        block = Block_V1(
            prev_block_hash,
            created_time,
            height,
            transactions,
            rejected_transactions_hashes,
            signatures,
        )

        try:
            session.add(block)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_block_by_height(
        height: int = 1,
    ) -> dict:
        "Get Iroha block from database by height"
        block_result = {}
        try:
            block = session.query(Block_V1).filter_by(height=height)
            block_result = block.__dict__
        except:
            _print("No Block Found")
        finally:
            return block_result

    @staticmethod
    def get_block_by_hash(block_hash):
        # check whether auth token has been blacklisted
        block = session.query(Block_V1).filter_by(height=block_hash)
        return block.__dict__

    @staticmethod
    def get_last_block():
        # check whether auth token has been blacklisted
        "Get Iroha block from database by height"
        block_result = {}
        try:
            block = block = (
                session.query(Block_V1).order_by(Block_V1.height.desc()).first()
            )
            block_result = block.__dict__
        except:
            raise
        finally:
            return block_result


try:
    base.metadata.create_all(db)
except:
    _print("[bold red]Could not connect to DB")
    user_choice = click.prompt(
        "Do you want to start a Docker Services locally? \nThis uses the docker-compose file located locally. [Y/n]",
        show_choices=["Y", "n"],
    )
    if str(user_choice).upper() == "Y":
        start_postgres_docker()
        _print(
            "[bold green]Started Postgres & Redis. \nPlease Restart CLi[/bold green]"
        )
        time.sleep(15)
        sys.exit()
    else:
        _print("[bold red]\nPlease check DB and Redis config[/bold red]")
    sys.exit()