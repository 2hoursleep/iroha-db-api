#!/usr/bin/python3
from modules.functions import IrohaBlockAPI
from modules import click, _print
from modules.menu_text import menu_text, welcome_msg
import os


@click.group()
def cli():
    pass


@cli.command(name="cli")
@click.option(
    "-a",
    "--account_id",
    type=str,
    envvar="ACCOUNT_ID",
    help="your Iroha Account ID including Domain Name \n e.g: 2hoursleep@iroha",
)
@click.option(
    "-ip",
    "--iroha_host",
    type=str,
    default="localhost:50051",
    envvar="IROHA_HOST",
    help="Iroha Node Address IP:PORT or DNS \n e.g: localhost:50051",
)
@click.option(
    "-pk",
    "--private_key",
    envvar="IROHA_V1_API_SECRET",
    type=str,
    help="your Account ID for Keypair file",
)
def main(account_id, iroha_host, private_key):
    "Command Line Interface for Block DB API"
    _print(welcome_msg)
    if not account_id:
        account_id = click.prompt("Please enter the API AccountID e.g. admin@test")
    if not private_key:
        try:
            private_key_file = f"./{account_id}.priv"
            private_key = open(private_key_file, "rb+").read()
        except:
            private_key = os.getenv(
                "IROHA_V1_API_SECRET",
                "164879bd94411cb7c88308b6423f7dde1e6df19a98961c8aebf7d70990ade5b7",
            )
    # parse blocks once - checks if blocks exists if none runs test
    # runs backround task for parsing blocks & servering rest api
    # export data by range to json file
    try:
        iroha_api = IrohaBlockAPI(
            api_user=account_id, private_key=private_key, iroha_host=iroha_host
        )
        cli_active = True
        main_menu(iroha_api, cli_active)
    except:
        _print("Something went wrong")
        raise


def main_menu(iroha_api, cli_active):
    while cli_active:
        _print(menu_text)
        user_choice = click.prompt(
            "Please Select Your Option", show_choices=["1", "2", "3"]
        )
        if user_choice == "1":
            _print(f"[bold green]Starting Genesis Block Parsing...[/bold green]")
            iroha_api.parse_genesis_iroha_block_to_db()
        elif user_choice == "2":
            scan_range = click.prompt(
                "How many blocks must be parsed?", default=100, type=int
            )
            iroha_api.run_block_paser(scan_range)
        else:
            cli_active = False


@cli.command(name="parse")
@click.option(
    "-a",
    "--account_id",
    type=str,
    help="your Account ID for Keypair file",
)
def parse_iroha_blocks_to_db(account_id):
    "Parse Blocks to DB - Requires height"


if __name__ == "__main__":
    cli()
