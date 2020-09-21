# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app_settings = os.getenv("APP_SETTINGS", "project.server.config.DevelopmentConfig")
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
db2 = SQLAlchemy(app)

# Import Auth Routes / Views
# from project.server.auth.views import auth_blueprint

from project.server.blocks.views import blocks_blueprint

# Register Blueprint
# app.register_blueprint(auth_blueprint)
app.register_blueprint(blocks_blueprint)

with app.app_context():
    db.create_all()
