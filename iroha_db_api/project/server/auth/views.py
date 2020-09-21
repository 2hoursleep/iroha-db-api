# project/server/auth/views.py
# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView
from project.server import bcrypt, db
from project.server.iroha.accounts import (
    iroha_health_check,
    register_account,
    submit_tx_to_iroha,
)
from project.server.models import BlacklistToken, User

auth_blueprint = Blueprint("auth", __name__)


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        user = User.query.filter_by(email=post_data.get("email")).first()
        if iroha_health_check():
            if not user:
                try:
                    username = post_data.get("username")
                    public_key = post_data.get("publicKey")
                    domain = post_data.get("publicKey")
                    account_id = username + "@" + domain
                    register_account.delay(
                        username=username, domain=domain, public_key=public_key
                    )
                    user = User(
                        email=post_data.get("email"),
                        password=post_data.get("password"),
                        account_id=account_id,
                        public_key=public_key,
                    )
                    # insert the user
                    db.session.add(user)
                    db.session.commit()
                    responseObject = {
                        "status": "success",
                        "message": "Successfully registered.",
                    }
                    return make_response(jsonify(responseObject)), 201
                except Exception as e:
                    responseObject = {
                        "status": "fail",
                        "message": "Some error occurred. Please try again.",
                    }
                    return make_response(jsonify(responseObject)), 401
            else:
                responseObject = {
                    "status": "fail",
                    "message": "User already exists. Please Log in.",
                }
                return make_response(jsonify(responseObject)), 202
        else:
            responseObject = {
                "status": "fail",
                "message": "Blockchain Service is offline. Please Contact Support or wait a few minutes and try again",
            }
            return make_response(jsonify(responseObject)), 405


class LoginAPI(MethodView):
    """
    User Login Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        if iroha_health_check():
            try:
                print(post_data)
                user = User.query.filter_by(account_id=post_data["account_id"]).first()
                # write login tx to iroha
                print(f"user {user}")
                account_id = user.account_id
                transaction = post_data.get("transaction")
                # print(transaction)
                transaction["payload"]["reducedPayload"]["commands"] = transaction[
                    "payload"
                ]["reducedPayload"].pop("commandsList")
                transaction["signatures"] = transaction.pop("signaturesList")

                if user and bcrypt.check_password_hash(
                    user.password, post_data.get("password")
                ):
                    auth_token = user.encode_auth_token(user.id)
                    if auth_token:
                        submit_tx_to_iroha(account_id, transaction)
                        responseObject = {
                            "status": "success",
                            "email": user.email,
                            "message": "Successfully logged in.",
                            "auth_token": auth_token.decode(),
                        }
                        return make_response(jsonify(responseObject)), 200
                else:
                    responseObject = {
                        "status": "fail",
                        "message": "User does not exist.",
                    }
                    return make_response(jsonify(responseObject)), 404
            except Exception as e:
                print(e)
                responseObject = {"status": "fail", "message": "Try again"}
                return make_response(jsonify(responseObject)), 500
        else:
            responseObject = {
                "status": "fail",
                "message": "Blockchain Service is offline. Please Contact Support or wait a few minutes and try again",
            }
            return make_response(jsonify(responseObject)), 405


class UserAPI(MethodView):
    """
    User Resource
    """

    def get(self):
        # get the auth token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[0]
            except IndexError:
                responseObject = {
                    "status": "fail",
                    "message": "Bearer token malformed.",
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ""
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                responseObject = {
                    "status": "success",
                    "data": {
                        "user_id": user.id,
                        "email": user.email,
                        "account_id": user.account_id,
                        "admin": user.admin,
                        "registered_on": user.registered_on,
                    },
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {"status": "fail", "message": resp}
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return make_response(jsonify(responseObject)), 401


class LogoutAPI(MethodView):
    """
    Logout Resource
    """

    def post(self):
        # get auth token
        auth_header = request.headers.get("Authorization")
        print(auth_header)
        if auth_header:
            auth_token = auth_header.split(" ")[0]
        else:
            auth_token = ""
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        "status": "success",
                        "message": "Successfully logged out.",
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {"status": "fail", "message": e}
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {"status": "fail", "message": resp}
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return make_response(jsonify(responseObject)), 403


# define the API resources
registration_view = RegisterAPI.as_view("register_api")
login_view = LoginAPI.as_view("login_api")
user_view = UserAPI.as_view("user_api")
logout_view = LogoutAPI.as_view("logout_api")

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    "/auth/register", view_func=registration_view, methods=["POST"]
)
auth_blueprint.add_url_rule("/auth/login", view_func=login_view, methods=["POST"])
auth_blueprint.add_url_rule("/auth/user", view_func=user_view, methods=["GET"])
auth_blueprint.add_url_rule("/auth/logout", view_func=logout_view, methods=["POST"])
