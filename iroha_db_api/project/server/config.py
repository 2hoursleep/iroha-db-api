# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os

basedir = os.path.abspath(os.path.dirname(__file__))
# SQL Alchemy Driver; Postgres is being used

# API Db
postgres_local_base = "postgresql://postgres:docker@localhost:5433/"
# Change Database Name Here
database_name = "iroha_blocks_db"

api_db_pwd = os.getenv("API_DB_PASSWORD")
api_user_id = os.getenv("API_DB_USER")

api_db_host = os.getenv("API_DB_HOST")
api_db_port = os.getenv("API_DB_PORT")
api_db_name = os.getenv("API_DB")

API_DB_URI = (
    f"postgresql://{api_user_id}:{api_db_pwd}@{api_db_host}:{api_db_port}/{api_db_name}"
)


wsv_pwd = os.getenv("IROHA_WSV_DB_PASSWORD")
user_id = os.getenv("IROHA_WSV_DB_USER")

wsv_host = os.getenv("IROHA_WSV_DB_HOST")
wsv_port = os.getenv("IROHA_WSV_DB_PORT")
wsv_db = os.getenv("IROHA_WSV_DB")

IROHA_WSV_DB_URI = f"postgresql://{user_id}:{wsv_pwd}@{wsv_host}:{wsv_port}/{wsv_db}"


class BaseConfig:
    """Base configuration."""

    SECRET_KEY = os.getenv("API_SECRET_KEY", "my_precious")
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = API_DB_URI
    SQLALCHEMY_BINDS = {"api": SQLALCHEMY_DATABASE_URI, "iroha_wsv": IROHA_WSV_DB_URI}


class TestingConfig(BaseConfig):
    """Testing configuration."""

    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name + "_test"
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SECRET_KEY = "my_precious"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql:///example"
