import requests
from typing import Optional
from models.coin import Coin


def fetch_data(coin_pair: str) -> Optional[Coin]:
    url = "https://api3.binance.com/api/v3/ticker/24hr"
    params = {"symbol": coin_pair}

    response = requests.get(url=url, params=params)
    if 200 <= response.status_code < 300:
        return Coin(response.json())
    return None
