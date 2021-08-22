class CoinGeckoCoin:
    name = ""
    thumbnail = ""
    price = ""
    ath = ""
    market_cap = ""
    change_in_24h = ""
    last_updated = ""

    def __init__(self, coingecko_response: dict):
        self.name = coingecko_response['name']
        self.rank = coingecko_response['market_cap_rank']
        self.thumbnail = coingecko_response['image']['thumb']
        self.price = f"{coingecko_response['market_data']['current_price']['usd']} USD"
        self.ath = f"{coingecko_response['market_data']['ath']['usd']} USD"
        self.market_cap = f"{coingecko_response['market_data']['market_cap']['usd']:,} USD"
        self.change_in_24h = f"{coingecko_response['market_data']['price_change_percentage_24h']}%"
        self.last_updated = coingecko_response['market_data']['last_updated']
        self.last_updated = self.last_updated.replace("T", " ").replace("Z", " ")
