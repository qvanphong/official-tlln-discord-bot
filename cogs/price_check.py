import re

from discord import Embed
from discord.ext import commands

from checkers import global_checker
from helpers.coingecko_helper import CoinGeckoHelper


class PriceCheck(commands.Cog, name="Check giá"):
    def __init__(self, bot):
        self.bot = bot
        self.coingecko_helper = CoinGeckoHelper()

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if global_checker.from_config_server(message):

            match = re.search(r"^\?([a-zA-Z0-9]*)$", message.content, re.IGNORECASE)
            if match is not None and match.group(1) is not None:
                coin_name = match.group(1)
                result = self.coingecko_helper.fetch_coin_info(coin_name)

                if result is None:
                    await message.channel.send(f"Không tìm thấy coin {coin_name}")
                else:
                    embed = Embed(color=0x0DDEFB, title=f"{result.price} *({result.change_in_day})*") \
                        .set_author(name=result.symbol,
                                    icon_url=result.thumbnail) \
                        .set_footer(text=f"Sử dụng !mk {coin_name} để xem thêm chi tiết")
                    await message.channel.send(embed=embed)

    @commands.command(name="mk")
    async def market_info(self, ctx, coin_name):
        result = self.coingecko_helper.fetch_coin_info(coin_name)

        if result is None:
            await ctx.send(f"Không tìm thấy coin {coin_name}")
        else:
            embed = Embed(color=0x0DDEFB,
                          description=f"Không có thứ hạng cho **{result.name}**" if result.rank is None
                          else f"**{result.name}** được xếp hạng **#{result.rank}** trên CoinGecko") \
                .set_author(name=f"{result.name} ({result.symbol})",
                            icon_url=result.thumbnail) \
                .set_thumbnail(url=result.large_image) \
                .set_footer(text=f"Cập nhật lần cuối {result.last_updated}",
                            icon_url="https://static.coingecko.com/s/coingecko-logo-d13d6bcceddbb003f146b33c2f7e8193d72b93bb343d38e392897c3df3e78bdd.png")

            embed.add_field(name="Chi tiết", value=f"Tổng cung: {result.total_supply}\n"
                                                   f"Tổng cung lưu hành: {result.circulating_supply}\n"
                                                   f"Vốn hóa: {result.market_cap}\n"
                                                   f"Khối lượng giao dịch: {result.total_volume}", inline=False)

            embed.add_field(name="Giá", value=f"Hiện tại: {result.price}\n"
                                              f"ATH: {result.ath}", inline=True)

            embed.add_field(name="Thay đổi", value=f"Ngày: {result.change_in_day}\n"
                                                   f"Tuần: {result.change_in_week}\n"
                                                   f"Tháng: {result.change_in_month}", inline=True)

            await ctx.send(embed=embed)

    def bot_check(self, ctx):
        return global_checker.from_config_server(ctx)
