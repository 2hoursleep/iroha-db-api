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
from project.server import bcrypt, db
from project.server.iroha.accounts import submit_query_to_iroha, submit_tx_to_iroha
from project.server.models import BlacklistToken, User

brvs_blueprint = Blueprint("brvs", __name__)


class IrohaQueryAPI(MethodView):
    """
    Iroha Query Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        account_id = post_data.get("account_id")
        transaction = post_data.get("transaction")
        print(transaction)
        # transaction["payload"]["reducedPayload"]["commands"] = transaction["payload"]["reducedPayload"].pop("commandsList")
        # transaction["signatures"] = transaction.pop("signaturesList")
        result = submit_query_to_iroha(account_id, transaction)
        responseObject = {
            "result": result,
            "status": "success",
            "message": "Successfully registered.",
        }
        return make_response(jsonify(responseObject)), 201


class IrohaTxAPI(MethodView):
    """
    Iroha Account Detail Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        account_id = post_data.get("account_id")
        transaction = post_data.get("transaction")
        transaction["payload"]["reducedPayload"]["commands"] = transaction["payload"][
            "reducedPayload"
        ].pop("commandsList")
        transaction["signatures"] = transaction.pop("signaturesList")
        submit_tx_to_iroha(account_id, transaction)
        responseObject = {"status": "success", "message": "Successfully registered."}
        return make_response(jsonify(responseObject)), 201


query_api = IrohaQueryAPI.as_view("iroha_query_api")

tx_api = IrohaTxAPI.as_view("iroha_tx_api")
# add Rules for API Endpoints

brvs_blueprint.add_url_rule("/submit/tx", view_func=tx_api, methods=["POST"])

brvs_blueprint.add_url_rule("/submit/query", view_func=query_api, methods=["POST"])
