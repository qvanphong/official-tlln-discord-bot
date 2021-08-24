class BTCDominance:
    percentage = 0.0
    percentage_change_24h = 0.0

    def __init__(self, data: dict) -> None:
        self.percentage = f"{data['market_cap_percentage']['btc']:.2f}%"
        self.percentage_change_24h = f"{data['market_cap_change_percentage_24h_usd']:.2f}%"
