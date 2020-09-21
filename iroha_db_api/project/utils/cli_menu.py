# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from project.utils import _print, click
from project.utils.menu_text import menu_text


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
        elif user_choice == "3":
            scan_range = click.prompt(
                "How often in seconds should the cro", default=100, type=int
            )
            iroha_api.run_block_paser(scan_range)
        else:
            cli_active = False
