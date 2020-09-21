# Iroha DB API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Python 3.8](https://img.shields.io/badge/python-3.8-red.svg)](https://www.python.org/downloads/release/python-380/) [![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)


This tool started as a proof-of-concept and forms part of a template starter-kit for projects requiring further interaction with [Hyperledger Iroha](https://www.iroha.com) Distributed Ledger.

**Please note.** The project is a work-in-progress and is **not** an official Hyperledger or Iroha approved solution.

## Purpose

Iroha is an excellent robust enterprise grade permissioned blockchain, inhertedly, performing analytical tasks require a custom solution as Iroha's query system uses the World State View, which is the current state of the blockchain, and actual transactional information resides in the block storage.

Self-service Business Intellegence tools like Microsoft PowerBi & Tableu along with spreadsheet tools like Excel have allowed end-users (especially in the entreprise enviroment) to easliy connect to Databases and Rest APIs to perform further ETL tasks and conduct analysis. It is their ease of use and powerful capabilities that convince 

Whilst the tools mentioned above are **not** Open Source, they are clearly some of the market-leaders in the analytics space. API's allow us to interface progamatically with applications, and one of the goals of this and companion projects are to provide an open-source alternatives to assist with PoC developments or actual onboarding on Iroha as a production 

*Currently **Microsoft Powerbi Desktop** is free to download and use. An example Powerbi file will be added soon*

This project aims to be a proof-of-concept that Hyperledger Iroha's data can be analysed by relevant audiences in a manner that complies with existing and new privacy laws.

## Requirements

The below mandatory list is required for this repository to work.

Poetry manages the Python virtual env. and installs the required depencies, alternatively a requirements.txt file has been included for installing using pip.

Development and deployment using Docker is **highly** recommended.

### Mandatory

* Hyperledger Iroha v1.x
* Python 3.8
* Postgres

### Optional - Recommended

* Docker
* Docker-comppose
* Poetry

## How it works

Iroha allows an authorized account (can_get_blocks or root permission) to query the block storage directly.
By performing simple ETL techniques data can be parsed to a more traditional SQL or NoSQL Database and stored in tables or collections respectively.

**IMPORTANT** If no auth or access restriction methods are implemented users will be able to access all data.

This example uses Postgres as a database, with an Rest API developed using Flask.
Future examples will include alternative database implentations.

A cronjob periodially queries Iroha using the getBlocks query, storing them into a sql table. The Rest API exposes endpoints (optionally authorized) allowing data to be sent in JSON Format.

All database actions are done using SQLAlchemy. If you require extra functionality e.g add other databases or tables, additional sql operations, Sqlalchemy has excellent documentation with loads of tutorials available for free.

**Please Note** The Rest API is an optional method for consuming the data. You can connect to the database directly using normal odbc methods.

## Installation

### Docker Method


1) Build docker images:
    
    *optionally change image tag*

    ```console

    ./build-image.sh
    ```
2) Modify docker-compose env variables accordignly:

    ```docker-compose
    version: '3.5'
    services:
    api:
        volumes:
        - ./iroha_db_api:/app
        ports:
        - "5000:5000"
        environment:
        - FLASK_APP=manage.py
        - FLASK_DEBUG=1
        - IROHA_ACCOUNT_ID=admin@test
        - IROHA_HOST=localhost:50051
        - 'RUN=flask run --host=0.0.0.0 --port=5000'
        command: flask run --host=0.0.0.0 --port=5000
        # Infinite loop, to keep it alive, for debugging
        # command: bash -c "while true; do echo 'sleeping...' && sleep 10; done"
    worker:
        volumes:
        - ./iroha_db_api:/app
        environment:
        - IROHA_DB_CRON=2
        - IROHA_ACCOUNT_ID=admin@test
        - IROHA_HOST=localhost:50051
        command: python3 manage.py worker
    ```

3) Start with docker-compose:

    **stating all continers**

    ```console

    docker-compose up
    or
    docker-compose up -d
    ```

    Depending on the blockstore size, this might take a few minutees to sync up to current World State View height.


4) Use HTTP requests lib to query endpoints:

    ```console

    curl -x http://localhost:5000/v1/data/blocks/

    ```

### Local Development

Development was done using Python 3.8, however any release including Python 3.6 or newer should work.

#### Pip (Without Poetry)

* Using a virtualenv is recommended to isolate packages from the global python modules

1) Install requirements.txt using pip
    ```console

    pip3 install -r requirements.txt
    ```

2) Change to iroha_db_api directory
    ```console

    cd iroha_db_api/
    ```


3) Ensure **Database & Iroha** are both online then run manage.py:

    using --help flag to display arguments
    ```console

    python3 manage.py worker --help 
    
    Usage: manage.py worker [OPTIONS]

    Starts DB Cronjob Worker

    Options:
    -a, --account_id TEXT    Iroha Account ID including Domain Name  e.g:
                             2hoursleep@iroha

    -i, --iroha_host TEXT    Iroha Node Address IP:PORT or DNS  e.g:
                             localhost:50051

    -pk, --private_key TEXT  Private key
    -t, --timer INTEGER      Cron worker frequency
    --help                   Show this message and exit.
    ```
