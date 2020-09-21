# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os

from project.server.iroha.utils.iroha_tools import IrohaClient, submit_query, submit_tx

account_id = os.getenv("IROHA_ACCOUNT_ID")
iroha_host = os.getenv("IROHA_HOST_ADDRESS")

admin = IrohaClient(creator_account=account_id, iroha_host=iroha_host)


def iroha_health_check():
    global admin
    global account_id
    status = False
    try:
        result = admin.get_account(account_id)
        print(f"iroha health check {result}")
        status = True
    except Exception as error:
        print(f"iroha health chech failed \n {error}")
        status = False
    finally:
        return status


def submit_tx_to_iroha(account_id, transaction):
    result = submit_tx(account_id, transaction)
    print(result)
    return result


def submit_query_to_iroha(account_id, transaction):
    result = submit_query(account_id, transaction)
    return result


def register_account(self, username, domain, public_key):
    global admin
    print(f"username: {username} \n public_key: {public_key}")
    public_key = bytes(public_key, "utf-8")
    try:
        admin.create_new_account(
            account_name=username, domain=domain, public_key=public_key
        )
        account_id = username + "@" + domain
        admin.init_test_balance_batch(account_id=account_id)
    except Exception as error:
        print("unable to create user on iroha")
        print(error)
        self.retry(countdown=5, exc=error, max_retries=1)


def admin_sign_tx(transaction):
    global admin
    admin.sign_and_submit_tx(transaction=transaction)
    return {"status": "SUCCESS"}


def write_user_data(username, domain, key, value):
    global admin
    account_id = username + domain
    admin.set_account_detail(account_id, key, value)


def increase_domain_assets(asset_id, qty):
    global admin
    admin.add_asset_qty(asset_id, qty)


def send_assets(account_id, recipient, asset_id, description, qty):
    global admin
    admin.transfer_asset(account_id, recipient, asset_id, description, qty)


def read_user_data(username, domain, key, value):
    global admin
    account_id = username + domain
    admin.set_account_detail(account_id, key, value)
