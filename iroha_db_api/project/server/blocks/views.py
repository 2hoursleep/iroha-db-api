# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import json
import logging
import os

from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView
from project.server import db
from project.server.iroha.accounts import submit_query_to_iroha, submit_tx_to_iroha
from project.server.models import Block_V1
from project.server.schemas import Block

blocks_blueprint = Blueprint("blocks", __name__)


class BlockAPI(MethodView):
    """
    Iroha Block API
    """

    def get(self):
        "Get all blocks"
        results = Block_V1.query.all()
        response = []
        for result in results:
            block = Block.from_orm(result)
            response.append(block.dict())
        responseObject = {
            "result": response,
            "status": "success",
            "message": "Successfully returned blocks.",
        }
        return make_response(jsonify(responseObject)), 201

    def post(self):
        "Get block data by height"
        post_data = request.get_json()
        height = int(post_data.get("height"))
        result = Block_V1.query.filter_by(height=height).first()
        block = Block.from_orm(result)
        responseObject = {
            "result": block.dict(),
            "status": "success",
            "message": "Successfully registered.",
        }
        return make_response(jsonify(responseObject)), 201


class Transactions(MethodView):
    """
    Iroha Block API
    """

    def get(self):
        "Get all transactions"
        results = Block_V1.query.all()
        response = []
        for result in results:
            db_block = Block.from_orm(result)
            block = db_block.dict()
            print(block["payload"]["transactions"])
            response.append(block.dict())
        responseObject = {
            "result": response,
            "status": "success",
            "message": "Successfully returned blocks.",
        }
        return make_response(jsonify(responseObject)), 201

    def post(self):
        "Get block data by height"
        post_data = request.get_json()
        print("tx data request")
        height = int(post_data.get("height"))
        result = Block_V1.query.filter_by(height=height).first()
        block = Block.from_orm(result).dict()
        print(block.keys())
        responseObject = {
            "result": block,
            "status": "success",
            "message": "Successfully returned block.",
        }
        return make_response(jsonify(responseObject)), 201


block_query_api = BlockAPI.as_view("block_api")

tx_query_api = Transactions.as_view("transactions_history_api")

blocks_blueprint.add_url_rule(
    "/v1/data/blocks/", view_func=block_query_api, methods=["GET", "POST"]
)

blocks_blueprint.add_url_rule(
    "/v1/data/tx-history/", view_func=tx_query_api, methods=["GET", "POST"]
)
