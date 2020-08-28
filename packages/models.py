from sqlalchemy import Column, String, Integer, DateTime
import datetime
from .db import db, session, base
from sqlalchemy.dialects.postgresql.json import JSONB
from dataclasses import dataclass


@dataclass
class Block_V1(base):
    __tablename__ = "iroha_blocks"

    block_hash = Column(String, primary_key=True)
    height = Column(Integer)
    payload = Column(JSONB)
    tx_number = Column(Integer)
    added_on = Column(DateTime)

    def __init__(self, block_hash: str, height: int, payload: JSONB, tx_number: int):
        self.block_hash = block_hash
        self.height = height
        self.payload = payload
        self.tx_number = tx_number
        self.added_on = datetime.datetime.now()

    def __repr__(self):
        return f"<id: Block Hash: {self.block_hash} added \nHeight {self.height}"

    @staticmethod
    def add_block(block_hash, height, payload, tx_number):
        # check whether auth token has been blacklisted
        block = Block_V1(block_hash, height, payload, tx_number)
        session.add(block)
        session.commit()

    @staticmethod
    def get_block_by_height(height: int = 1,):
        # check whether auth token has been blacklisted
        block = session.query(Block_V1).filter_by(height=height)
        return block.__dict__

    @staticmethod
    def get_block_by_hash(block_hash):
        # check whether auth token has been blacklisted
        block = session.query(Block_V1).filter_by(height=block_hash)
        return block.__dict__

    @staticmethod
    def get_tx_by_command(command: str):
        # check whether auth token has been blacklisted
        block = session.query(Block_V1).filter_by(height=command)
        return block.__dict__


base.metadata.create_all(db)
