import re
from typing import Optional

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

            price_query_match = re.search(r"^\?([a-zA-Z0-9]+)$", message.content, re.IGNORECASE)
            if price_query_match is not None and price_query_match.group(1) is not None:
                coin_name = price_query_match.group(1).lower()
                result = self.coingecko_helper.fetch_coin_info(coin_name)

                if result is None:
                    await message.channel.send(f"Không tìm thấy coin {coin_name}")
                else:
                    embed = Embed(color=0x0DDEFB, title=f"${result.price:,.2f} *({result.change_in_day:.2f}%)*") \
                        .set_author(name=result.symbol,
                                    icon_url=result.thumbnail) \
                        .set_footer(text=f"Sử dụng !mk {coin_name} để xem thêm chi tiết")
                    await message.channel.send(embed=embed)
            else:
                rate_match = re.search(r"^([1-9]+(\.[0-9]*)?)\s*([a-zA-Z0-9]+)\s*=\s*(\?|bn)\s*([a-zA-Z0-9]+)$",
                                       message.content)
                if rate_match is not None:
                    await self.coin_rate(message.channel,
                                         float(rate_match.group(1)),
                                         rate_match.group(3),
                                         rate_match.group(5))

    @commands.command(name="mk",
                      brief="Lấy thông tin thị trường của 1 coin cụ thể",
                      description="Nhập tên 1 coin cụ thể để lấy thông tin về thị trường của coin đó.\n"
                                  "VD: !mk neo")
    async def market_info(self, ctx, coin_name):
        result = self.coingecko_helper.fetch_coin_info(coin_name.lower())

        if result is None:
            await ctx.send(f"Không tìm thấy coin {coin_name}")
        else:
            total_supply = f"{result.total_supply:,.0f}" if result.total_supply is not None else "∞"
            embed = Embed(color=0x0DDEFB,
                          description=f"Không có thứ hạng cho **{result.name}**" if result.rank is None
                          else f"**{result.name}** được xếp hạng **#{result.rank}** trên CoinGecko") \
                .set_author(name=f"{result.name} ({result.symbol})",
                            icon_url=result.thumbnail) \
                .set_thumbnail(url=result.large_image) \
                .set_footer(text=f"Cập nhật lần cuối {result.last_updated}",
                            icon_url="https://static.coingecko.com/s/coingecko-logo-d13d6bcceddbb003f146b33c2f7e8193d72b93bb343d38e392897c3df3e78bdd.png")

            embed.add_field(name="Chi tiết", value=f"Tổng cung: {total_supply} {result.symbol}\n"
                                                   f"Tổng cung lưu hành: {result.circulating_supply:,} {result.symbol}\n"
                                                   f"Vốn hóa: ${result.market_cap:,} USD\n"
                                                   f"Khối lượng giao dịch: ${result.total_volume:,}", inline=False)

            embed.add_field(name="Giá", value=f"Hiện tại: ${result.price:,.2f}\n"
                                              f"ATH: ${result.ath:,.2f}", inline=True)

            embed.add_field(name="Thay đổi", value=f"Ngày: {result.change_in_day:,.2f}%\n"
                                                   f"Tuần: {result.change_in_week:,.2f}%\n"
                                                   f"Tháng: {result.change_in_month:,.2f}%", inline=True)

            await ctx.send(embed=embed)

    @commands.command(name="rate",
                      brief="Chuyển đổi rate giữa 2 coin khác nhau.",
                      description="Command này tương tự như xxx coin_a = coin_b.\n"
                                  "VD: !rate 10 gas neo (tương tự 10 gas = ? neo)\n"
                                  "VD: !rate gas neo (tương tự 1 gas = ? neo)")
    async def coin_rate(self, ctx, amount: Optional[float] = 1.0, coin_a="", coin_b=""):
        rate = self.coingecko_helper.get_coin_rate(amount, coin_a.lower(), coin_b.lower())
        if rate is not None:
            embed = Embed(color=0x0DDEFB)

            embed.add_field(name=f"Rate {coin_a.upper()}/{coin_b.upper()}",
                            value=f"{amount} {coin_a.upper()} = {rate:.2f} {coin_b.upper()}", inline=True)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Coin nhập vào không hợp lệ")

    @commands.command(name="dmn",
                      brief="Lấy dominance của Bitcoin")
    async def btc_dominance(self, ctx):
        dominance = self.coingecko_helper.get_global_info()
        embed = Embed(color=0x0DDEFB)
        embed.set_author(name="Bitcoin Dominance")

        embed.add_field(name="Dominance", value=dominance.percentage, inline=True)
        embed.add_field(name="Thay đổi trong 24h", value=dominance.percentage_change_24h, inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(PriceCheck(bot))
