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

    tick = 1  # represent for time read message
    difference_percentage = 5  # difference to trigger a message

    bots: [Member] = {}  # list of bots, use to rename
    temp_btc = {'coin_name': 'btc', 'last_price': '',
                'time': ''}  # This will save BTC coin everytime, use to calculate BTC pair to USD
    coins = {'NEOUSDT': 'neo',
             'FIROUSDT': 'firo',
             'BTCUSDT': 'btc',
             'ZENUSDT': 'zen',
             'DASHUSDT': 'dash',
             'GASBTC': 'gas',
             'ARKBTC': 'ark',
             }  # List of support coins

    def __init__(self, bot: commands.Bot):
        self.discord_bot = bot

    # Read Binance wss message
    # Check if it can send alert because have difference
    async def on_message(self, message):
        json_message = json.loads(message)
        coin_pair = json_message["data"]["s"]
        coin_name = self.coins[coin_pair]
        currency = "BTC" if "BTC" in coin_pair and coin_pair != "BTCUSDT" else "USD"
        await self.send_alert(coin_name=coin_name, current_price_data=json_message, currency=currency)

        if self.tick == 5:
            await self.update_bot_name(json_message, currency)
            self.tick = 1
        else:
            self.tick += 1

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
            message = "**{coin_name}** vừa {signal} {:.2f}% trên sàn Binance. " \
                      "Từ **{:{prec}} USD** {up_down} **{:{prec}} USD**" \
                .format(difference,
                        float(old_price["last_price"]) if currency == 'USD' else old_price_usd,
                        float(current_price) if currency == 'USD' else new_price_usd,
                        coin_name=coin_name.upper(),
                        signal="tăng" if price_changed_status == 1 else "giảm",
                        up_down="lên" if price_changed_status == 1 else "xuống",
                        prec=".2f")

            embed_message = Embed(color=util.get_ember_color(price_changed_status), description=message)
            embed_message.set_author(name=util.get_alert_type(price_changed_status),
                                     icon_url=util.get_coin_image(coin_name))
            embed_message.set_thumbnail(url=util.get_coin_image(coin_name))

            await self.discord_bot \
                .get_guild(env.SERVER_ID) \
                .get_channel(util.get_channel_id(coin_name)) \
                .send(embed=embed_message)

            price_db.insert_to_db(coin_name, current_price, time)
            return {'coin_name': coin_name, 'last_price': current_price, 'time': time}

        return old_price

    # Start binance websocket, đồng thời load lại các dữ liệu giá cữ trước khi chạy
    async def start(self):

        client = await tornado.websocket.websocket_connect(url=env.BINANCE_WS_URL)
        while True:
            message = await client.read_message()
            await self.on_message(message)

    async def update_bot_name(self, price_data, currency='USD'):
        if len(self.bots) == 0:
            guild = self.discord_bot.get_guild(env.SERVER_ID)

            for pair, coin_name in self.coins.items():
                bot = guild.get_member(util.get_bot_id(coin_name))
                self.bots[pair] = bot

        pair = price_data["data"]["s"]
        price = float(price_data["data"]["c"])
        bot = self.bots[pair]
        if currency == 'USD':
            await bot.edit(nick="${:.2f}".format(price))
        else:
            await bot.edit(nick="${:.2f}".format(price * float(self.temp_btc["last_price"])))
