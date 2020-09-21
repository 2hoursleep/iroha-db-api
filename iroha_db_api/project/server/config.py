# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os

basedir = os.path.abspath(os.path.dirname(__file__))
# SQL Alchemy Driver; Postgres is being used
postgres_local_base = "postgresql://postgres:docker@localhost:5433/"
# Change Database Name Here
database_name = "iroha_blocks_db"

IROHA_WSV_DB_URI = "postgresql://postgres:mysecretpassword@localhost:5432/iroha_data"


class BaseConfig:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious")
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name
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
