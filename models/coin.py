import time


class Coin:
    # Trading pair
    symbol = ""

    # Last trading price
    price = 0.0

    # Change in 24h
    change_24h = 0.0

    # Volume of base asset
    volume = 0.0

    # Volume of quote asset
    quote_volume = 0.0

    # Time of this Coin object created, stand of event time
    time = 0

    def __init__(self, json: dict):
        self.symbol = json["symbol"]
        self.price = float(json["lastPrice"])
        self.volume = float(json["volume"])
        self.quote_volume = float(json["quoteVolume"])
        self.change_24h = float(json["priceChangePercent"])
        self.time = int(time.time())
