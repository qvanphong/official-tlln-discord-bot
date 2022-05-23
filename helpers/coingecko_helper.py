from typing import Optional

from pycoingecko import CoinGeckoAPI

from models.coingecko_coin import CoinGeckoCoin
from models.btc_dominance import BTCDominance


class CoinGeckoHelper():
    coin_list = {}
    coingecko = CoinGeckoAPI()

    def __init__(self):
        for coin in self.coingecko.get_coins_list():
            self.coin_list[coin['symbol']] = coin['id']

        self.coin_list['usd'] = 'tether'
        self.coin_list['vnd'] = 'binance-vnd'
        self.coin_list['gas'] = 'gas'
        self.coin_list['luna'] = 'terra-luna'

    def fetch_coin_info(self, symbol) -> Optional[CoinGeckoCoin]:
        if symbol in self.coin_list:
            # coin_data = self.coingecko.get_price(ids=self.coin_list[symbol],
            #                                      vs_currencies='usd',
            #                o                      include_market_cap=True,
            #               /|\                     include_24hr_vol=True,
            #               /\                      include_24hr_change=True,
            #                                      include_last_updated_at=True)
            coin_data = self.coingecko.get_coin_by_id(id=self.coin_list[symbol],
                                                      localization='false',
                                                      tickers=False,
                                                      market_data=True,
                                                      community_data=False,
                                                      developer_data=False,
                                                      sparkline=False)

            return CoinGeckoCoin().from_advanced(coin_data)
        return None

    def get_global_info(self) -> BTCDominance:
        coin_data = self.coingecko.get_global()
        return BTCDominance(coin_data)

    def get_coin_rate(self, coin_a_amount, coin_a, coin_b):
        if coin_a not in self.coin_list:
            return None
        if coin_b not in self.coin_list:
            return None

        coin_a = self.coin_list[coin_a]
        coin_b = self.coin_list[coin_b]

        result = self.coingecko.get_price(ids=[coin_a, coin_b], vs_currencies='usd')
        return coin_a_amount * result[coin_a]['usd'] / result[coin_b]['usd']
