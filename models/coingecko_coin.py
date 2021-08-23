class CoinGeckoCoin:
    name = ""
    symbol = ""
    rank = ""
    thumbnail = ""
    large_image = ""

    price = ""
    ath = ""

    market_cap = ""
    change_in_day = ""
    change_in_week = ""
    change_in_month = ""

    total_volume = ""
    total_supply = ""
    circulating_supply = ""

    last_updated = ""

    def __init__(self, coingecko_response: dict):
        self.name = coingecko_response['name']
        self.symbol = coingecko_response['symbol'].upper()
        self.rank = coingecko_response['market_cap_rank']
        self.thumbnail = coingecko_response['image']['thumb']
        self.large_image = coingecko_response['image']['large']

        self.price = f"${coingecko_response['market_data']['current_price']['usd']:,} USD"
        self.ath = f"${coingecko_response['market_data']['ath']['usd']:,} USD"

        self.market_cap = f"${coingecko_response['market_data']['market_cap']['usd']:,} USD"
        self.change_in_day = f"{coingecko_response['market_data']['price_change_percentage_24h']:.2f}%"
        self.change_in_week = f"{coingecko_response['market_data']['price_change_percentage_7d']:.2f}%"
        self.change_in_month = f"{coingecko_response['market_data']['price_change_percentage_30d']:.2f}%"

        total_supply = "∞" if coingecko_response['market_data']['total_supply'] is None else \
            f"{int(coingecko_response['market_data']['total_supply']):,}"
        self.total_supply = f"{total_supply} {self.symbol}"
        self.total_volume = f"${coingecko_response['market_data']['total_volume']['usd']:,} USD"
        self.circulating_supply = f"{coingecko_response['market_data']['circulating_supply']:,} {self.symbol}"

        self.last_updated = coingecko_response['market_data']['last_updated']
        self.last_updated = self.last_updated.replace("T", " ").replace("Z", " ")
