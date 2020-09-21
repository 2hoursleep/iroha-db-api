# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os
import sys
import threading
import unittest

import schedule
from project.utils import _print, click
from project.utils.functions import IrohaBlockAPI


@click.group()
def cli():
    pass


@cli.command(name="worker")
@click.option(
    "-a",
    "--account_id",
    type=str,
    envvar="IROHA_ACCOUNT_ID",
    help="Iroha Account ID including Domain Name \n e.g: 2hoursleep@iroha",
)
@click.option(
    "-i",
    "--iroha_host",
    type=str,
    default="localhost:50051",
    envvar="IROHA_HOST",
    help="Iroha Node Address IP:PORT or DNS \n e.g: localhost:50051",
)
@click.option(
    "-pk",
    "--private_key",
    envvar="IROHA_DB_API_SECRET",
    type=str,
    help="your Account ID for Keypair file",
)
@click.option(
    "-t",
    "--timer",
    envvar="IROHA_DB_CRON",
    type=str,
    help="your Account ID for Keypair file",
)
def start_api(account_id: str, iroha_host: str, private_key: str, timer):
    """Starts REST API"""
    if not account_id:
        account_id = click.prompt("Please enter the API AccountID e.g. admin@test")
    if not private_key:
        try:
            # look for file first
            private_key_file = f"./{account_id}.priv"
            private_key = open(private_key_file, "rb+").read()
        except FileNotFoundError:
            _print("Private key file not found")
            private_key = click.prompt(
                f"Please enter private key for AccountID: {account_id}"
            )
            if not private_key:
                use_demo_key = click.prompt(
                    f"Do you want to use the demo private key for: {account_id}?"
                )
                if str(use_demo_key).lower() == "y":
                    private_key = "164879bd94411cb7c88308b6423f7dde1e6df19a98961c8aebf7d70990ade5b7"
                else:
                    _print("Exiting...\nPlease set all required params and restart.")
                    sys.exit()
    if not timer:
        timer = click.prompt("Block Parser Cron Job in Minutes")
        os.environ["IROHA_DB_CRON"] = timer
    try:
        timer = int(timer)
        iroha_api = IrohaBlockAPI(
            api_user=account_id, private_key=private_key, iroha_host=iroha_host
        )
        _print(f"Current Iroha WSV Height: {iroha_api.get_wsv_height()}")
        schedule.every(timer).minutes.do(iroha_api.cron_block_parser)
    except:
        raise

    worker_active = True
    while worker_active:
        schedule.run_pending()

        # thread = threading.Thread(target=schedule.run_pending(), args=())
        # thread.daemon = True
        # thread.start()


if __name__ == "__main__":
    cli()
