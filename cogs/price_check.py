import re

from discord import Embed
from discord.ext import commands

from helpers.coingecko_helper import CoinGeckoHelper


def is_price_command():
    async def predicate(ctx: commands.Context):
        pass

    return commands.check(predicate)


class PriceCheck(commands.Cog, name="price_check"):
    def __init__(self, bot):
        self.bot = bot
        self.coingecko_helper = CoinGeckoHelper()

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        match = re.search(r"^\?([a-zA-Z0-9]*)$", message.content, re.IGNORECASE)
        if match is not None and match.group(1) is not None:
            result = self.coingecko_helper.fetch_coin(match.group(1))
            if result is None:
                await message.channel.send(f"Không tìm thấy coin {match.group(1)}")
            else:
                embed = Embed(color=0x0DDEFB) \
                    .set_author(name=f"{result.name} #{result.rank}", icon_url=result.thumbnail) \
                    .set_thumbnail(url=result.thumbnail) \
                    .set_footer(text=f"Cập nhật lần cuối {result.last_updated}",
                                icon_url="https://static.coingecko.com/s/coingecko-logo-d13d6bcceddbb003f146b33c2f7e8193d72b93bb343d38e392897c3df3e78bdd.png")

                embed.add_field(name="Giá hiện tại", value=f"**{result.price}**", inline=False)
                embed.add_field(name="ATH", value=f"**{result.ath}**", inline=False)
                embed.add_field(name="Vốn hóa thị trường", value=f"**{result.market_cap}**", inline=False)
                embed.add_field(name="Thay đổi trong 24 giờ", value=f"**{result.change_in_24h}**", inline=False)

                await message.channel.send(embed=embed)


@commands.command()
async def pong(self, ctx):
    await ctx.send("ping")
