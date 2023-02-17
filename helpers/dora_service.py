import requests
from typing import Optional
from models.coin import Coin


def get_wallet_balance(address: str, symbol: str):
    url = "https://dora.coz.io/api/v1/neo3/mainnet/balance/" + address

    response = requests.get(url=url)
    if 200 <= response.status_code < 300:
        json_response = response.json()
        for assets in json_response:
            if assets["symbol"] == symbol:
                return assets["balance"]
    return None


def get_wallet_balance(address: str):
    url = "https://dora.coz.io/api/v1/neo3/mainnet/balance/" + address

    response = requests.get(url=url)
    if 200 <= response.status_code < 300:
        results = {}

        json_response = response.json()
        for assets in json_response:
            results[assets["symbol"]] = assets["balance"]

        return results

    return {}
