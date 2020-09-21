# Copyright 2020 by Farren Jackson, Distributed Ledger Solutions ZA.
# All rights reserved.
# This file is part of the Iroha Database API & CLI Tool,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import json
import uuid
from typing import Dict, List

from pydantic import BaseModel


class Block(BaseModel):
    height: int
    prev_block_hash: str
    created_time: str
    transactions: List[Dict] = []
    rejected: List[Dict] = []
    signatures: List[Dict] = []
    rejected_transactions_hashes: List[str] = []

    class Config:
        orm_mode = True


class Blocks(BaseModel):
    name: str
    admin_name: str
    participants: List[str] = []
