import requests
import json
import pandas as pd

headers = {
                "Content-Type":"application/json",
                "Accept":"application/json",
            }

def test_get_genesis_block(height=1):
    r = requests.post(
            url="http://0.0.0.0:5000/v1/data/blocks/",
            headers = headers,
            data = json.dumps({
                "height": height
                }
            )
        )
    assert r.status_code == 201

def test_get_txs(height=1):
    r = requests.post(
            url="http://0.0.0.0:5000/data/tx-history/",
            headers = headers,
            data = json.dumps({
                "height": height
                }
            )
        )
    assert r.status_code == 201