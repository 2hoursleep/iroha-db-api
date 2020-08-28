from packages.block_collector import IrohaBlockAPI
from packages.models import Block_V1
from packages.db import session
import os
import json


class IrohaAuth(object):
    def __init___(self):
        self.private_key = os.getenv(
            "IROHA_V1_API_SECRET",
            "164879bd94411cb7c88308b6423f7dde1e6df19a98961c8aebf7d70990ade5b7",
        )
        self.api_user = os.getenv("IROHA_V1_API_ACC_ID", "admin@iroha")
        self.iroha_host = os.getenv("IROHA_V1_API_HOST", "localhost:50051")
        self.iroha_block_api = IrohaBlockAPI(
            creator_account=self.api_user,
            private_key=self.private_key,
            iroha_host=self.iroha_host,
        )


class Oracle(object):
    """
    Calls Iroha v1 getBlocks query.
    requires accountId with can_get_blocks permission
    :params height int
    :retuns block dict
    """
    def __init__(self):
        self.iroha_client = IrohaAuth()

    def get_iroha_blocks(self, height: int = 1) -> dict:
        """
        Calls Iroha v1 getBlocks query.
        requires accountId with can_get_blocks permission
        :params height int
        :retuns block dict
        """
        unpased_block = self.iroha_client.iroha_block_api.get_blocks(height=height)
        block = json.loads(unpased_block)

        # Payload & other block information are nested and mapped

        payload = block["blockResponse"]["block"]["blockV1"]["payload"]["transactions"][
            0
        ]["payload"]["reducedPayload"]["commands"]
        block_hash = block["blockResponse"]["block"]["blockV1"]["payload"][
            "prevBlockHash"
        ]
        height = block["blockResponse"]["block"]["blockV1"]["payload"]["height"]
        txNumber = block["blockResponse"]["block"]["blockV1"]["payload"]["txNumber"]
        parsed_block = {
            "height": height,
            "block_hash": block_hash,
            "txNumber": txNumber,
            "payload": payload,
        }

        return parsed_block

    def add_block_to_db(self, parsed_block: dict) -> None:
        try:
            iroha_block = Block_V1.add_block(
                height=parsed_block["height"],
                block_hash=parsed_block["block_hash"],
                payload=parsed_block["payload"],
                tx_number=parsed_block["txNumber"],
            )
            print("block added")
            print(iroha_block)
        except Exception as error:
            print(f"noooooo\n{error}")
