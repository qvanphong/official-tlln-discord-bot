import asyncio
from discord import Embed, Member
from discord.ext import commands

import repository.price_repository as price_db
from utils import env, price_alert_utils as util
import tornado.websocket
import json

try:
    import thread
except ImportError:
    import _thread as thread


class PriceAlert:
    discord_bot = None  # Discord bot client

    difference_percentage = env.PERCENTAGE_DIFFERENCE  # difference to trigger a message
    update_nickname_interval = env.UPDATE_COINBOT_INTERVAL  # difference to trigger a message

    bots: [Member] = {}  # list of bots, use to rename
    temp_btc = {'coin_name': 'btc', 'last_price': '',
                'time': ''}  # This will save BTC coin everytime, use to calculate BTC pair to USD
    coins = {'NEOUSDT': {'name': 'neo', 'value': 0.0},
             'FIROUSDT': {'name': 'firo', 'value': 0.0},
             'BTCUSDT': {'name': 'btc', 'value': 0.0},
             'ZENUSDT': {'name': 'zen', 'value': 0.0},
             'DASHUSDT': {'name': 'dash', 'value': 0.0},
             'GASBTC': {'name': 'gas', 'value': 0.0},
             'ARKBTC': {'name': 'ark', 'value': 0.0},
             }  # List of support coins, name stand for correct coin name, value stand for latest price.

    def __init__(self, bot: commands.Bot):
        self.discord_bot = bot

    # Read Binance wss message
    # Check if it can send alert because have difference
    async def on_message(self, message):
        json_message = json.loads(message)
        coin_pair = json_message["data"]["s"]
        coin_name = self.coins[coin_pair]['name']
        currency = "BTC" if "BTC" in coin_pair and coin_pair != "BTCUSDT" else "USD"
        self.coins[coin_pair]['value'] = await self.send_alert(coin_name=coin_name, current_price_data=json_message,
                                                               currency=currency)

    def check_price_change(self, old_price, current_price):
        difference = abs(old_price - current_price) / ((old_price + current_price) / 2) * 100

        if difference < self.difference_percentage:
            return [0, difference]
        else:
            pump_or_dump = 1 if old_price < current_price else -1
            return [pump_or_dump, difference]

    async def send_alert(self, coin_name, current_price_data, currency='USD'):
        old_price = price_db.get_coin_by_name(coin_name)
        current_price = current_price_data["data"]["c"]
        time = current_price_data["data"]["E"]

        # save btc price every second for convert USD
        if coin_name == 'btc':
            self.temp_btc['last_price'] = current_price
            self.temp_btc['time'] = time

        # If old price does exist, insert new one.
        if old_price is None:
            price_db.insert_to_db(coin_name, current_price, time)
            old_price = price_db.get_coin_by_name(coin_name)

        # Convert BTC pair to USD
        if currency == 'BTC':
            if self.temp_btc["last_price"] != '':
                old_price_usd = float(old_price["last_price"]) * float(self.temp_btc["last_price"])
                new_price_usd = float(current_price) * float(self.temp_btc["last_price"])
            else:
                return
        else:
            old_price_usd = float(old_price["last_price"])
            new_price_usd = float(current_price)

        price_changed_status, difference = self.check_price_change(old_price_usd, new_price_usd)

        # If price status is PUMP (1) or DUMP (-1), then send a message
        if price_changed_status != 0:
            message = "**{coin_name}** vừa {signal} {icon}{difference:.2f}% trên sàn Binance. " \
                .format(coin_name=coin_name.upper(),
                        signal="tăng" if price_changed_status == 1 else "giảm",
                        difference=difference,
                        icon="↗" if price_changed_status == 1 else "↘",)

            embed_message = Embed(color=util.get_ember_color(price_changed_status), description=message)
            embed_message.set_author(name=util.get_alert_type(price_changed_status),
                                     icon_url=util.get_coin_image(coin_name))
            embed_message.set_thumbnail(url=util.get_coin_image(coin_name))

            embed_message.add_field(name="Giá trước đó", value="**{:.2f} USD**".format(old_price_usd), inline=True)

            embed_message.add_field(name="Giá hiện tại", value="**{:.2f} USD**".format(new_price_usd), inline=True)

            embed_message.add_field(name="Thay đổi trong 24h",
                                    value="**{}%**".format(current_price_data["data"]["P"]),
                                    inline=False)

            await self.discord_bot \
                .get_guild(env.SERVER_ID) \
                .get_channel(util.get_channel_id(coin_name)) \
                .send(embed=embed_message)

            price_db.insert_to_db(coin_name, current_price, time)

        return new_price_usd

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
                if price is not None and price != 0.0:
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
