from sqlalchemy import Column, String, Integer, DateTime
import datetime

from sqlalchemy.util.langhelpers import dictlike_iteritems
from .db import db, session, base
from sqlalchemy.dialects.postgresql.json import JSONB
from dataclasses import dataclass


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

    def __init__(self, prev_block_hash: str, created_time: str ,height: int, transactions: JSONB, rejected_transactions_hashes: JSONB, signatures: JSONB) -> dict:
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
    def add_block(prev_block_hash, created_time ,height, transactions, rejected_transactions_hashes, signatures):
        # add Iroha block to database
        block = Block_V1(prev_block_hash, created_time ,height, transactions, rejected_transactions_hashes, signatures)
        
        try:
            session.add(block)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

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
    def get_last_block():
        # check whether auth token has been blacklisted
        block = session.query(Block_V1).order_by(Block_V1.height.desc()).first()
        print(block.height)
        return block.__dict__


base.metadata.create_all(db)
