import random

from discord import Embed
from discord.ext import commands


class FunCog(commands.Cog, name="Linh tinh", description="Các lệnh linh ta linh tinh"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pick",
                      brief="Chọn ngẫu nhiên các giá trị nhập vào",
                      description="Chọn ngẫu nhiên bằng cách nhập các lựa chọn, được cách nhau bởi dấu \",\"\n"
                                  "VD: !pick ARK lên 30$, ARK stable coin")
    async def pick(self, ctx, *, arg):
        args = arg.split(',')
        result = args[random.randint(0, len(args) - 1)]

        embed = Embed(color=0x0DDEFB)
        embed.add_field(name="Kết quả:", value=result)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(FunCog(bot))
