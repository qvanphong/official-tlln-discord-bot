import asyncio
from discord import Embed, Member
from discord.ext import commands

import repository.price_repository as price_db
from utils import env, price_alert_utils as util
from utils.price_alert_utils import  PriceStatus
import tornado.websocket
import json


# try:
#     import thread
# except ImportError:
#     import _thread as thread


class PriceAlert:
    # Discord bot client
    discord_bot = None

    # Difference to trigger a message
    difference_percentage = env.PERCENTAGE_DIFFERENCE

    # Difference to trigger a message
    update_nickname_interval = env.UPDATE_COINBOT_INTERVAL

    # List of bots, use to rename
    bots: [Member] = {}

    # This will save BTC coin everytime,
    # use to calculate BTC pair to USD
    temp_btc = {'coin_name': 'btc', 'last_price': ''}

    # Contains coin pair's information.
    # Name: normalize that coin's name
    # Value: latest price of this pair, but will save in USD if the pair is BTC
    coins = {'NEOUSDT': {'name': 'neo', 'value': 0.0},
             'FIROUSDT': {'name': 'firo', 'value': 0.0},
             'BTCUSDT': {'name': 'btc', 'value': 0.0},
             'ZENUSDT': {'name': 'zen', 'value': 0.0},
             'DASHUSDT': {'name': 'dash', 'value': 0.0},
             'GASBTC': {'name': 'gas', 'value': 0.0},
             'ARKBTC': {'name': 'ark', 'value': 0.0},
             'ETHUSDT': {'name': 'eth', 'value': 0.0},
             }  # List of support coins, name stand for correct coin name, value stand for latest price.

    def __init__(self, bot: commands.Bot):
        self.discord_bot = bot

    async def on_message(self, message):
        """
        Read Binance's wss message

        :param message: raw JSON message from wss
        """
        price_data = json.loads(message)
        coin_pair = price_data["data"]["s"]
        coin_name = self.coins[coin_pair]['name']
        currency = "BTC" if "BTC" in coin_pair and coin_pair != "BTCUSDT" else "USD"

        # save btc price every second for convert USD
        if coin_name == 'btc':
            self.temp_btc['last_price'] = price_data["data"]["c"]

        self.coins[coin_pair]['value'] = await self.compare_and_send(coin_name=coin_name, current_price_data=price_data,
                                                                     currency=currency)

    def has_difference(self, old_price, current_price):
        """
        Calculate the percentage between old and new price.

        :param old_price: old price
        :param current_price: new price
        :return: an array 2 with elements.
                1 is pump_or_dump is PriceStatus enum.
                2 is difference percentage
        """
        difference = abs(old_price - current_price) / ((old_price + current_price) / 2) * 100

        if difference < self.difference_percentage:
            return [PriceStatus.NOTHING, difference]
        else:
            pump_or_dump = PriceStatus.PUMP if old_price < current_price else PriceStatus.DUMP
            return [pump_or_dump, difference]

    async def compare_and_send(self, coin_name: str, current_price_data: dict, currency='USD'):
        """
        Compare the current_price_data with its old price,
        if there is a pump/dump then send a embed message to some channels

        :param coin_name: name of coins, passed from self.coins[]['name']
        :param current_price_data:  price data from wss sending to and parsed to dict
        :param currency: BTC or USD base on their pair
        :return: a new price in USD.
        """
        old_price_data = price_db.get_coin_by_name(coin_name)
        current_price = current_price_data["data"]["c"]
        time = current_price_data["data"]["E"]

        # If old price does exist, insert new one.
        if old_price_data is None:
            price_db.insert_to_db(coin_name, current_price, time)
            old_price_data = price_db.get_coin_by_name(coin_name)

        # Convert BTC pair to USD
        if currency == 'BTC':
            if self.temp_btc["last_price"] != '':
                old_price_usd = float(old_price_data["last_price"]) * float(self.temp_btc["last_price"])
                new_price_usd = float(current_price) * float(self.temp_btc["last_price"])
            else:
                return
        else:
            old_price_usd = float(old_price_data["last_price"])
            new_price_usd = float(current_price)

        price_status, difference = self.has_difference(old_price_usd, new_price_usd)

        # If price status is PUMP or DUMP, then send a message
        if price_status != PriceStatus.NOTHING:
            price_db.insert_to_db(coin_name, current_price, time)
            await self.send_price_alert(coin_name=coin_name,
                                        old_price=old_price_usd,
                                        new_price=new_price_usd,
                                        change_in_24=current_price_data["data"]["P"],
                                        price_status=price_status,
                                        difference=difference)
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
        coin_channel = util.get_channel_id(coin_name)

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
        if coin_channel is not None:
            await self.discord_bot \
                .get_guild(env.SERVER_ID) \
                .get_channel(util.get_channel_id(coin_name)) \
                .send(embed=embed_message)

        # Send to spam channel
        await self.discord_bot \
            .get_guild(env.SERVER_ID) \
            .get_channel(env.SPAM_CHANNEL) \
            .send(embed=embed_message)

        # Send to other coins channel
        await self.discord_bot \
            .get_guild(env.SERVER_ID) \
            .get_channel(env.OTHER_COINS_CHANNEL) \
            .send(embed=embed_message)

    # Update CoinBot's name.
    async def update_bot_name(self):
        while True:
            # Save bot to self.bots dict if this is first time run.
            if len(self.bots) == 0:
                guild = self.discord_bot.get_guild(env.SERVER_ID)
                for pair, value in self.coins.items():
                    bot = guild.get_member(util.get_bot_id(value['name']))
                    self.bots[pair] = bot

            for pair, bot in self.bots.items():
                price: float = self.coins[pair]['value']
                if bot is not None and price is not None and price != 0.0:
                    try:
                        await bot.edit(nick="{name} ${price:.2f}".format(name=bot.name, price=price))
                    except Exception as e:
                        print("Error occurs: ")
                        print(e)
            await asyncio.sleep(self.update_nickname_interval)

    # Start binance websocket.
    async def start(self):
        # create update_bot_name task and run separate.
        self.discord_bot.loop.create_task(self.update_bot_name())

        # Begin connect websocket and wait for new message.
        client = await tornado.websocket.websocket_connect(url=env.BINANCE_WS_URL)
        while True:
            message = await client.read_message()
            if message is not None:
                await self.on_message(message)
