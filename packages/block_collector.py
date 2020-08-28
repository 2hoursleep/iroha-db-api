import binascii

from binascii import Error
import json
import pprint
import iroha.primitive_pb2 as iroha_primitive
import iroha.queries_pb2 as queries_pb2
from google.protobuf.json_format import MessageToDict, MessageToJson, ParseDict
from iroha import Iroha, IrohaGrpc
from iroha import IrohaCrypto as ic


class IrohaBlockAPI(object):
    def __init__(self, creator_account, private_key, iroha_host):
        self.creator_account = creator_account
        self.iroha = Iroha(creator_account)
        self.ic = ic
        self.permissions = iroha_primitive
        self.user_private_key = private_key
        self.net = IrohaGrpc(iroha_host, timeout=60)  # limit time out

    def parse_result(message):
        result = MessageToJson(message=message, preserving_proto_field_name=True)
        return result

    def submit_transaction(self, transaction):
        hex_hash = str(binascii.hexlify(self.ic.hash(transaction)), "utf-8")
        tx_result = {}
        msg = f"[bold yellow]Transaction Hash:[/bold yellow] [bold green]{hex_hash}[/bold green] \n[bold yellow]Creator Account ID:[/bold yellow] [bold green]{transaction.payload.reduced_payload.creator_account_id}[/bold green]"
        print(msg)
        try:
            self.net.send_tx(transaction)
            tx_status = []
            for status in self.net.tx_status_stream(transaction):
                tx_status.append(status)
            tx_result = {
                "tx_hash": hex_hash,
                "tx_statuses": tx_status,
                "tx_result": tx_status[-1][0],
            }
            print(f"{tx_result}")
        except Exception as error:
            print(error)
            tx_result = {
                "tx_hash": hex_hash,
                "tx_statuses": [],
                "tx_result": "REJECTED",
            }
            print(tx_result)
        finally:
            return tx_result

    def stream_blocks(self):
        """
        Start incomming stream for new blocks
        """
        query = self.iroha.blocks_query()
        self.ic.sign_query(query, self.user_private_key)
        for block in self.net.send_blocks_stream_query(query):
            pprint("The next block arrived: {}".format(MessageToDict(block)), indent=1)

    def seed_tx(self, account_id, key, value):
        tx = self.iroha.transaction(
            [
                self.iroha.command(
                    "SetAccountDetail", account_id=account_id, key=key, value=value
                )
            ]
        )
        ic.sign_transaction(tx, self.user_private_key)
        self.submit_transaction(tx)

    def get_blocks(self, height=1):
        """
        Get iroha Blocks v1
        """
        query = self.iroha.query("GetBlock", height=height)
        ic.sign_query(query, self.user_private_key)
        response = self.net.send_query(query)
        data = MessageToJson(response)
        return data
