from typing import Optional

from pycoingecko import CoinGeckoAPI

from models.coingecko_coin import CoinGeckoCoin


class CoinGeckoHelper():
    coin_list = {}
    coingecko = CoinGeckoAPI()

    def __init__(self):
        for coin in self.coingecko.get_coins_list():
            self.coin_list[coin['symbol']] = coin['id']

    def fetch_coin(self, symbol) -> Optional[CoinGeckoCoin]:
        if symbol in self.coin_list:
            # coin_data = self.coingecko.get_price(ids=self.coin_list[symbol],
            #                                      vs_currencies='usd',
            #                                      include_market_cap=True,
            #                                      include_24hr_vol=True,
            #                                      include_24hr_change=True,
            #                                      include_last_updated_at=True)
            coin_data = self.coingecko.get_coin_by_id(id=self.coin_list[symbol],
                                                      localization='false',
                                                      tickers=False,
                                                      market_data=True,
                                                      community_data=False,
                                                      developer_data=False,
                                                      sparkline=False)

            return CoinGeckoCoin(coin_data)
        return None
