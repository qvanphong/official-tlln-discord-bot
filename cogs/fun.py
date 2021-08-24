import random

from discord import Embed
from discord.ext import commands


class FunCog(commands.Cog, name="Linh tinh", description="Các lệnh linh ta linh tinh"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pick", description="Chọn ngẫu nhiên các giá trị nhập vào")
    async def pick(self, ctx, *, arg):
        args = arg.split(',')
        result = args[random.randint(0, len(args) - 1)]

        embed = Embed(color=0x0DDEFB)
        embed.add_field(name="Kết quả:", value=result)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(FunCog(bot))
