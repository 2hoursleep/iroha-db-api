from packages.block_collector import IrohaBlockAPI
from packages.models import Block_V1
from packages.db import session
from packages.cronjob import huey
import os
import json
import asyncio


huey.start()

private_key = os.getenv(
    "IROHA_V1_API_SECRET",
    "164879bd94411cb7c88308b6423f7dde1e6df19a98961c8aebf7d70990ade5b7",
)
api_user = os.getenv("IROHA_V1_API_ACC_ID", "admin@iroha")
iroha_host = os.getenv("IROHA_V1_API_HOST", "localhost:50051")
iroha_block_api = IrohaBlockAPI(
    creator_account=api_user, private_key=private_key, iroha_host=iroha_host,
)
@huey.task()
def parse_iroha_blocks_to_db(height:int = 1) -> None:
    """
    Iroha Block Parser
    :param height: Address of the Sender,
    :param return_block: Returns block in JSON Format
    :return: None if return_block is false
    """
    block = json.loads(iroha_block_api.get_blocks(height=height))
    
    try:
        height = block["blockResponse"]["block"]["blockV1"]["payload"]["height"]
        prev_block_hash = block["blockResponse"]["block"]["blockV1"]["payload"]["prevBlockHash"]
        created_time = block["blockResponse"]["block"]["blockV1"]["payload"]["createdTime"]
        signatures = block["blockResponse"]["block"]["blockV1"]["signatures"]
        try:
            rejected_transactions_hashes = block["blockResponse"]["block"]["blockV1"]["payload"]["rejectedTransactionsHashes"]
        except:
            rejected_transactions_hashes = []
        try:
            transactions = block["blockResponse"]["block"]["blockV1"]["payload"]["transactions"]
        except:
            transactions = []
        Block_V1.add_block(
            created_time=created_time,
            height=height,
            prev_block_hash=prev_block_hash,
            transactions=transactions,
            rejected_transactions_hashes=rejected_transactions_hashes,
            signatures=signatures)
    except Exception as error:
        print(error)


def parse_genesis_iroha_blocks_to_db(height:int = 1):
    """
    
    """
    try:
        raw_block = iroha_block_api.get_blocks(height=height)
        block = json.loads(raw_block)
        transactions = block["blockResponse"]["block"]["blockV1"]["payload"]["transactions"]
        prev_block_hash = block["blockResponse"]["block"]["blockV1"]["payload"]["prevBlockHash"]
        height = block["blockResponse"]["block"]["blockV1"]["payload"]["height"]
        txNumber = block["blockResponse"]["block"]["blockV1"]["payload"]["txNumber"]
        Block_V1.add_block(
            created_time='0',
            height=height,
            prev_block_hash=prev_block_hash,
            transactions=transactions,
            rejected_transactions_hashes=[],
            signatures=[])
    except Exception as error:
        print(error)


def start_up():
    # get last block from db if none start from 1
    try:
        parse_genesis_iroha_blocks_to_db()
    except:
        print('Genesis block already exists')
    finally:
        last_block = Block_V1.get_last_block()
        return last_block
    

#res = load_blocks_to_database.schedule(args=(10, 20), delay=2)
#print(res())

# Stop the scheduler. Not strictly necessary, but a good idea.

def start_parser(last_height: int, scan_range: int =100):
    curent_height = last_height
    end_height = curent_height + scan_range
    while curent_height < end_height:
        parse_iroha_blocks_to_db(height=curent_height)
        curent_height += 1
        print(f'parsed block {curent_height}')

last_block = start_up()
last_height = last_block["height"]
start_parser(last_height,100)
huey.stop()