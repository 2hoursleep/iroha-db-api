from packages.block_collector import IrohaBlockAPI
from packages.models import Block_V1
from packages.db import session
import os
import json

private_key = os.getenv(
    "IROHA_V1_API_SECRET",
    "164879bd94411cb7c88308b6423f7dde1e6df19a98961c8aebf7d70990ade5b7",
)
api_user = os.getenv("IROHA_V1_API_ACC_ID", "admin@iroha")
iroha_host = os.getenv("IROHA_V1_API_HOST", "localhost:50051")
iroha_block_api = IrohaBlockAPI(
    creator_account=api_user, private_key=private_key, iroha_host=iroha_host,
)


def parse_iroha_blocks_to_db(height: int = 1):
    """
    
    """
    block = json.loads(iroha_block_api.get_blocks(height=1))
    payload = block["blockResponse"]["block"]["blockV1"]["payload"]["transactions"][0][
        "payload"
    ]["reducedPayload"]["commands"]
    block_hash = block["blockResponse"]["block"]["blockV1"]["payload"]["prevBlockHash"]
    height = block["blockResponse"]["block"]["blockV1"]["payload"]["height"]
    txNumber = block["blockResponse"]["block"]["blockV1"]["payload"]["txNumber"]

    iroha_block = Block_V1.add_block(
        height=height, block_hash=block_hash, payload=payload, tx_number=txNumber
    )

    print(iroha_block)
