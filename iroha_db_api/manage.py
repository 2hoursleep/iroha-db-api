# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os
import threading
import unittest
import sys

import schedule

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

import schedule
from project.server import app, db, models
from project.utils import _print, click
from project.utils.cli_menu import main_menu
from project.utils.functions import IrohaBlockAPI
from project.utils.menu_text import welcome_msg


migrate = Migrate(app, db)


@click.group()
def cli():
    pass


@cli.command(name="cli")
@click.option(
    "-a",
    "--account_id",
    type=str,
    envvar="IROHA_USER",
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
    envvar="IROHA_DB_API_SECRET",
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
            script_dir = os.path.dirname(__file__)
            rel_path = f"{account_id}.priv"
            private_key_file = os.path.join(script_dir, rel_path)
            private_key = open(private_key_file, "rb+").read()
        except FileNotFoundError:
            _print("Private key not found")
            sys.exit()
    try:
        iroha_api = IrohaBlockAPI(
            api_user=account_id, private_key=private_key, iroha_host=iroha_host
        )
        print(iroha_api.get_wsv_height())
        cli_active = True
        main_menu(iroha_api, cli_active)
    except Exception as error:
        _print(error)


@cli.command(name="test")
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover("project/tests", pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command(name="cov")
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover("project/tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, "tmp/coverage")
        COV.html_report(directory=covdir)
        print("HTML version: file://%s/index.html" % covdir)
        COV.erase()
        return 0
    return 1


@cli.command(name="create-db")
def create_db():
    """Creates the db tables."""
    db.create_all()


@cli.command(name="drop-db")
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@cli.command(name="api")
@click.option(
    "-a",
    "--account_id",
    type=str,
    envvar="IROHA_USER",
    help="Iroha Account ID including Domain Name \n e.g: admin@test",
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
    envvar="IROHA_API_SECRET",
    type=str,
    help="Iroha private key",
)
@click.option(
    "-p",
    "--port",
    type=int,
    help="Port to run API on default 5000",
)
def start_api(account_id: str, iroha_host, private_key):
    """Starts REST API"""
    if not account_id:
        account_id = click.prompt("Please enter the API AccountID e.g. admin@test")
    if not private_key:
        try:
            script_dir = os.path.dirname(__file__)
            rel_path = f"{account_id}.priv"
            private_key_file = os.path.join(script_dir, rel_path)
            private_key = open(private_key_file, "rb+").read()
            os.environ["IROHA_DB_API_SECRET"] = private_key
        except FileNotFoundError:
            _print("[bold red]Private key file not found[/bold red]")
            sys.exit()
    os.environ["IROHA_HOST"] = iroha_host
    app.run()


@cli.command(name="worker")
@click.option(
    "-a",
    "--account_id",
    type=str,
    envvar="IROHA_USER",
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
    envvar="IROHA_API_SECRET",
    type=str,
    help="Private key",
)
@click.option(
    "-t",
    "--timer",
    envvar="API_DB_CRON",
    type=int,
    help="Cron worker frequency",
)
def start_worker(account_id: str, iroha_host: str, private_key: str, timer):
    """Starts DB Cronjob Worker"""

    if not account_id:
        account_id = click.prompt("Please enter the API AccountID e.g. admin@test")
    if not private_key:
        try:
            # look for file first
            script_dir = os.path.dirname(__file__)
            rel_path = f"{account_id}.priv"
            private_key_file = os.path.join(script_dir, rel_path)
            private_key = open(private_key_file, "rb+").read()
        except FileNotFoundError:
            _print("Private key file not found")
            private_key = click.prompt(
                f"Please enter private key for AccountID: {account_id}"
            )
            if not private_key:
                _print("Exiting...\nPlease set all required params and restart.")
                sys.exit()
    if not timer:
        timer = click.prompt("Block Parser Cron Job in Minutes")
        os.environ["API_DB_CRON"] = timer
    try:
        timer = int(timer)
        iroha_api = IrohaBlockAPI(
            api_user=account_id, private_key=private_key, iroha_host=iroha_host
        )
        _print(f"Current Iroha WSV Height: {iroha_api.get_wsv_height()}")
        schedule.every(timer).minutes.do(iroha_api.cron_block_parser)
    except Exception:
        _print(Exception)

    worker_active = True
    while worker_active:
        schedule.run_pending()


if __name__ == "__main__":
    cli()
