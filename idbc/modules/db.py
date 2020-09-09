from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQL Alchemy Driver;
# Postgres is being used
postgres_local_base = "postgresql://postgres:docker@localhost:5433/"
# Database Name
database_name = "iroha_blocks_db"
db_string = postgres_local_base + database_name

db = create_engine(db_string)
base = declarative_base()
# create a configured "Session" class
Session = sessionmaker(bind=db)

# create a Session
session = Session()
