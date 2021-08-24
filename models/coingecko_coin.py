class CoinGeckoCoin:
    name = ""
    symbol = ""
    rank = ""
    thumbnail = ""
    large_image = ""

    price = 0.0
    ath = 0.0

    market_cap = 0.0
    change_in_day = 0.0
    change_in_week = 0.0
    change_in_month = 0.0

    total_volume = 0.0
    total_supply = 0.0
    circulating_supply = 0.0

    last_updated = ""

    def __init__(self, name="",
                 symbol="",
                 rank="",
                 thumbnail="",
                 large_image="",
                 price="",
                 ath="",
                 market_cap="",
                 change_in_day="",
                 change_in_week="",
                 change_in_month="",
                 total_volume="",
                 total_supply="",
                 circulating_supply="",
                 last_updated=""):
        self.name = name
        self.symbol = symbol
        self.rank = rank
        self.thumbnail = thumbnail
        self.large_image = large_image

        self.price = price
        self.ath = ath

        self.market_cap = market_cap
        self.change_in_day = change_in_day
        self.change_in_week = change_in_week
        self.change_in_month = change_in_month

        self.total_supply = total_supply
        self.total_volume = total_volume
        self.circulating_supply = circulating_supply

        self.last_updated = last_updated

    def from_advanced(self, coingecko_response: dict):
        self.name = coingecko_response['name']
        self.symbol = coingecko_response['symbol'].upper()
        self.rank = coingecko_response['market_cap_rank']
        self.thumbnail = coingecko_response['image']['thumb']
        self.large_image = coingecko_response['image']['large']

        self.price = coingecko_response['market_data']['current_price']['usd']
        self.ath = coingecko_response['market_data']['ath']['usd']

        self.market_cap = coingecko_response['market_data']['market_cap']['usd']
        self.change_in_day = coingecko_response['market_data']['price_change_percentage_24h']
        self.change_in_week = coingecko_response['market_data']['price_change_percentage_7d']
        self.change_in_month = coingecko_response['market_data']['price_change_percentage_30d']

        self.total_supply = coingecko_response['market_data']['total_supply']
        self.total_volume = coingecko_response['market_data']['total_volume']['usd']
        self.circulating_supply = coingecko_response['market_data']['circulating_supply']

        self.last_updated = coingecko_response['market_data']['last_updated'].replace("T", " ").replace("Z", "")

        return self
