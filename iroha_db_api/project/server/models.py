# project/server/models.py
# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


import datetime
from dataclasses import dataclass

import jwt
from project.server import app, bcrypt, db, db2
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.automap import automap_base

# Init reflection from WSV DB
db2.reflect(app=app)
db2.Model.metadata.reflect(db2.engine)
AutoMapModel = automap_base(db2.Model)

# For additional tables copy model and change table_name


@dataclass
class Wsv_Block_Info(AutoMapModel):
    __bind_key__ = "iroha_wsv"
    __tablename__ = "top_block_info"


@dataclass
class Block_V1(db.Model):
    __bind_key__ = "api"
    __tablename__ = "iroha_blocks"
    __table_args__ = {"extend_existing": True}

    prev_block_hash = db.Column(db.String)
    height = db.Column(db.Integer, primary_key=True)
    added_on = db.Column(db.DateTime)
    created_time = db.Column(db.String)
    signatures = db.Column(JSONB)
    rejected_transactions_hashes = db.Column(JSONB)
    transactions = db.Column(JSONB)

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
        return f"Block Height: {self.height}"

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
            db.session.add(block)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

    @staticmethod
    def get_block_by_height(
        height: int = 1,
    ) -> dict:
        "Get Iroha block from database by height"
        block_result = {}
        try:
            block = db.session.query(Block_V1).filter_by(height=height)
            block_result = block.__dict__
        except:
            raise
        finally:
            return block_result

    @staticmethod
    def get_block_by_hash(block_hash):
        block = db.session.query(Block_V1).filter_by(height=block_hash)
        return block.__dict__

    @staticmethod
    def get_last_block():
        "Get Iroha block from database by height"
        block_result = {}
        try:
            block = block = (
                db.session.query(Block_V1).order_by(Block_V1.height.desc()).first()
            )
            block_result = block.__dict__
        except:
            raise
        finally:
            return block_result


class User(db.Model):
    """ User Model for storing user related details """

    __bind_key__ = "api"
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    account_id = db.Column(db.String(255), unique=True, nullable=False)
    public_key = db.Column(db.String(255), unique=False, nullable=False)

    def __init__(self, email, password, account_id, public_key, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.account_id = account_id
        self.public_key = public_key

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token

        Token validilty determined by 'exp' field in paybload
        Current Duration 30 Minute

        :return: string
        """
        try:
            payload = {
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(days=0, minutes=30),
                "iat": datetime.datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(payload, app.config.get("SECRET_KEY"), algorithm="HS256")
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get("SECRET_KEY"))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return "Token blacklisted. Please log in again."
            else:
                return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "Signature expired. Please log in again."
        except jwt.InvalidTokenError:
            return "Invalid token. Please log in again."


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """

    __tablename__ = "blacklist_tokens"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return "<id: token: {}".format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False


AutoMapModel.prepare(db2.engine, reflect=True)
