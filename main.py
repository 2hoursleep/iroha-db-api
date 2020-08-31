from packages.block_collector import IrohaBlockAPI
from packages.models import Block_V1
from packages.db import session
import os
import json
import asyncio

private_key = os.getenv(
    "IROHA_V1_API_SECRET",
    "164879bd94411cb7c88308b6423f7dde1e6df19a98961c8aebf7d70990ade5b7",
)
api_user = os.getenv("IROHA_V1_API_ACC_ID", "admin@iroha")
iroha_host = os.getenv("IROHA_V1_API_HOST", "localhost:50051")
iroha_block_api = IrohaBlockAPI(
    creator_account=api_user, private_key=private_key, iroha_host=iroha_host,
)

def parse_iroha_blocks_to_db(height:int = 1):
    """
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


def async_parse_iroha_blocks_to_db(height:int = 1):
    """
    
    """
    try:
        raw_block = iroha_block_api.get_blocks(height=height)
        block = json.loads(raw_block)
        payload = block["blockResponse"]["block"]["blockV1"]["payload"]["transactions"][0][
            "payload"
        ]["reducedPayload"]["commands"]
        block_hash = block["blockResponse"]["block"]["blockV1"]["payload"]["prevBlockHash"]
        height = block["blockResponse"]["block"]["blockV1"]["payload"]["height"]
        txNumber = block["blockResponse"]["block"]["blockV1"]["payload"]["txNumber"]

        iroha_block = Block_V1.add_block(
            height=height,
            block_hash=block_hash,
            payload=payload,
            tx_number=txNumber
        )
        print(iroha_block)
    except Exception as error:
        print(error)

def load_blocks_to_database():
    import time

    start_time = time.time()
    cpu_start_time = time.process_time()

    for i in range(1, 350):
        parse_iroha_blocks_to_db(height=i)
        print(f'parsed block {i}')
    #total_real_time = time.time() - start_time
    total_cpu_time = time.process_time() - cpu_start_time
    print(total_cpu_time)
