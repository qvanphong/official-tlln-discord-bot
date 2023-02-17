from discord import Embed, Member, Color
from discord.ext import commands

import helpers.dora_service as dora_service
from helpers import price_alert_utils as util, app_config


class CEXGasBalanceWatcher:
    # Discord Bot
    discord_bot: commands.Bot = None

    cex_list = [
        {
            "cex_name": "Binance",
            "address": "NUqLhf1p1vQyP2KJjMcEwmdEBPnbCGouVp",
            "previous_balance": None,
            "balance": None,
            "symbol": "GAS"
        },
        {
            "cex_name": "Binance",
            "address": "NUqLhf1p1vQyP2KJjMcEwmdEBPnbCGouVp",
            "previous_balance": None,
            "balance": None,
            "symbol": "NEO"
        },
        {
            "cex_name": "OKX",
            "address": "NgJLhoyNBZPaEYDMm5vJbZHzdec6aTBQXU",
            "previous_balance": None,
            "balance": None,
            "symbol": "GAS"
        },
        {
            "cex_name": "OKX",
            "address": "NgJLhoyNBZPaEYDMm5vJbZHzdec6aTBQXU",
            "previous_balance": None,
            "balance": None,
            "symbol": "NEO"
        }
    ]

    gas_symbol = "GAS"

    def __init__(self, bot: commands.Bot):
        self.discord_bot = bot

    async def update_balance(self, first_init: bool = False):
        embed_message = Embed(color=Color.green(), description="CEX's GAS balance 1 hr changes")
        embed_message.set_author(name="CEX's GAS Balance", icon_url=util.get_coin_image("GAS"))

        loaded_address = {}
        has_header = False

        for cex_info in self.cex_list:
            wallet_address = cex_info["address"]
            symbol = cex_info["symbol"]

            # add to dict to prevent request again in same address, just use the existed one
            if wallet_address not in loaded_address:
                balance = dora_service.get_wallet_balance(cex_info["address"])
                loaded_address[wallet_address] = balance
            else:
                balance = loaded_address[wallet_address]

            if symbol not in balance:
                return

            symbol_balance = balance[symbol]
            cex_info["previous_balance"] = symbol_balance if cex_info["previous_balance"] is None else cex_info[
                "balance"]
            cex_info["balance"] = symbol_balance

            embed_message.add_field(name="Exchange" if has_header is False else "",
                                    value="**{}**".format(cex_info["cex_name"], symbol),
                                    inline=True)
            embed_message.add_field(name="From" if has_header is False else "",
                                    value="{:,.2f} {}".format(cex_info["previous_balance"], symbol),
                                    inline=True)
            embed_message.add_field(name="To" if has_header is False else "",
                                    value="{:,.2f} {}".format(symbol_balance, symbol),
                                    inline=True)
            has_header = True

        if first_init is False:
            coin_channel = util.get_channel_id("GAS")
            if coin_channel is not None:
                await self.discord_bot \
                    .get_guild(app_config.get_config("server_id")) \
                    .get_channel(util.get_channel_id("GAS")) \
                    .send(embed=embed_message)

    def _create_and_write_balance_to_file(self, file_path, balance):
        f = open(file_path, "x")
        f.write(str(balance))
        f.close()
