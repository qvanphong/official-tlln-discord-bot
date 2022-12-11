import asyncio
from discord import Embed, Member
from discord.ext import commands

import repositories.price_repository as price_db
from helpers import price_alert_utils as util, app_config, watcher_config, binance_service
from helpers.price_alert_utils import PriceStatus

from models.coin import Coin


class PriceWatcher:
    # Discord bot client
    discord_bot = None

    # Difference to trigger a message
    difference_percentage = watcher_config.get_config("percentage_difference")

    # Difference to trigger a message
    update_nickname_interval = watcher_config.get_config("update_coinbot_interval")

    # server's id
    server_id = app_config.get_config("server_id")

    # List of bots, use to rename
    bots: [Member] = {}

    # This will save BTC coin everytime,
    # use to calculate BTC pair to USD
    btc_price = 0.0

    # Contains coin pair's information.
    # Name: normalize that coin's name
    # Value: latest price of this pair, but will save in USD if the pair is BTC
    coins = {'NEOUSDT': {'name': 'NEO', 'value': 0.0},
             'FIROUSDT': {'name': 'FIRO', 'value': 0.0},
             'BTCUSDT': {'name': 'BTC', 'value': 0.0},
             'ZENUSDT': {'name': 'ZEN', 'value': 0.0},
             'DASHUSDT': {'name': 'DASH', 'value': 0.0},
             'GASBTC': {'name': 'GAS', 'value': 0.0},
             'ARKBUSD': {'name': 'ARK', 'value': 0.0},
             'ETHUSDT': {'name': 'ETH', 'value': 0.0},
             }  # List of support coins, name stand for correct coin name, value stand for latest price.

    def __init__(self, bot: commands.Bot):
        self.discord_bot = bot

    def has_difference(self, old_price, current_price):
        """
        Calculate the percentage between old and new price.

        :param old_price: old price
        :param current_price: new price
        :return: an array 2 with elements.
                1 is pump_or_dump is PriceStatus enum.
                2 is difference percentage
        """
        if ((old_price + current_price) / 2 == 0):
            return [PriceStatus.NOTHING, 0]
        difference = abs(old_price - current_price) / ((old_price + current_price) / 2) * 100

        if difference < self.difference_percentage:
            return [PriceStatus.NOTHING, difference]
        else:
            pump_or_dump = PriceStatus.PUMP if old_price < current_price else PriceStatus.DUMP
            return [pump_or_dump, difference]

    async def compare_and_send(self, coin_name: str, coin_info: Coin, currency='USD'):
        """
        Compare the current_price_data with its old price,
        if there is a pump/dump then send a embed message to some channels

        :param coin_name: name of coins, passed from self.coins[]['name']
        :param coin_info:  price data from wss sending to and parsed to dict
        :param currency: BTC or USD base on their pair
        :return: a new price in USD.
        """
        old_price_data = price_db.get_coin_by_name(coin_name)
        current_price = coin_info.price

        # If old price does exist, insert new one.
        if old_price_data is None:
            price_db.insert_to_db(coin_name, current_price, coin_info.time)
            return

        # Convert BTC pair to USD
        if currency == 'BTC':
            if self.btc_price != 0.0:
                old_price_usd = float(old_price_data["last_price"]) * float(self.btc_price)
                new_price_usd = float(current_price) * float(self.btc_price)
            else:
                return
        else:
            old_price_usd = float(old_price_data["last_price"])
            new_price_usd = float(current_price)

        price_status, difference = self.has_difference(old_price_usd, new_price_usd)

        # If price status is PUMP or DUMP, then send a message
        # if price_status != PriceStatus.NOTHING:
        #    price_db.insert_to_db(coin_name, current_price, coin_info.time)
        #    await self.send_price_alert(coin_name=coin_name,
        #                                old_price=old_price_usd,
        #                                new_price=new_price_usd,
        #                                change_in_24=coin_info.change_24h,
        #                                price_status=price_status,
        #                                difference=difference)
        return new_price_usd

    async def send_price_alert(self, coin_name: str, old_price: float, new_price: float, change_in_24: str,
                               price_status: PriceStatus, difference: float):
        """
        Create Embed Message and send it to some specific channels

        :param coin_name: normal name of coin
        :param old_price: old coin's price
        :param new_price: new coin's price
        :param change_in_24: difference in 24 hours.
        :param price_status: PriceStatus Enum. RePresent Pump or Dump or Nothing changed in price.
        :param difference: percentage difference.
        """
        message = "**{coin_name}** vừa {signal} {icon}{difference:.2f}% trên sàn Binance. " \
            .format(coin_name=coin_name.upper(),
                    signal="tăng" if price_status == PriceStatus.PUMP else "giảm",
                    difference=difference,
                    icon="➚" if price_status == PriceStatus.PUMP else "➘", )

        embed_message = Embed(color=util.get_ember_color(price_status), description=message)
        embed_message.set_author(name="Price alert",
                                 icon_url=util.get_coin_image(coin_name))
        embed_message.set_thumbnail(url=util.get_coin_image(coin_name))

        embed_message.add_field(name="Giá trước đó", value="**{:.2f} USD**".format(old_price), inline=True)

        embed_message.add_field(name="Giá hiện tại", value="**{:.2f} USD**".format(new_price), inline=True)

        embed_message.add_field(name="Thay đổi trong 24h",
                                value="**{}%**".format(change_in_24),
                                inline=False)

        # Send to specific coin channel
        coin_channel = util.get_channel_id(coin_name)
        if coin_channel is not None:
            await self.discord_bot \
                .get_guild(self.server_id) \
                .get_channel(util.get_channel_id(coin_name)) \
                .send(embed=embed_message)

        # Send to spam channel
        # await self.discord_bot \
        #     .get_guild(self.server_id) \
        #     .get_channel(app_config.get_config("spam_channel")) \
        #     .send(embed=embed_message)

        # Send to other coins channel
        # await self.discord_bot \
        #     .get_guild(self.server_id) \
        #     .get_channel(app_config.get_config("other_coins_channel")) \
        #     .send(embed=embed_message)

    async def update_bot_price(self, pair):
        """
        Update CoinBot's name as current price from self.coins data.
        :param pair: coin's trading pair
        """

        # Save bot to self.bots dict if this is first time run.
        if len(self.bots) == 0:
            guild = self.discord_bot.get_guild(self.server_id)
            for pair, value in self.coins.items():
                bot = guild.get_member(util.get_bot_id(value['name']))
                self.bots[pair] = bot

        bot = self.bots[pair]
        price: float = self.coins[pair]['value']
        if bot is not None and price is not None and price != 0.0:
            try:
                await bot.edit(nick="{name} ${price:.2f}".format(name=bot.name, price=price))
            except Exception as e:
                print(f"Error occurs: {e}")

    async def check_and_update_bot_name(self):
        """
        Check the current of every coin pair,
        send Price alert if there is difference equal or greater than config's value
        """
        for pair, value in self.coins.items():
            coin_info = binance_service.fetch_data(coin_pair=pair)

            if coin_info is not None:
                coin_name = value["name"]
                currency = "BTC" if "BTC" in coin_info.symbol and coin_info.symbol != "BTCUSDT" else "USD"

                # save btc price every second for convert to USD in any BTC pair
                if coin_name == "BTC":
                    self.btc_price = coin_info.price

                value['value'] = await self.compare_and_send(coin_name=coin_name,
                                                            coin_info=coin_info,
                                                            currency=currency)

                await self.update_bot_price(pair=pair)
