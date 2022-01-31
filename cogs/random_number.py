import random

import discord
from discord import Embed
from discord.ext import commands

from models.advanced_random import AdvancedRandomModel

def get_random_number(minimum, maximum):
    return random.randint(int(minimum), int(maximum))

class RandomNumberCog(commands.Cog, name="Chọn số ngẫu nhiên", description="Các lệnh hỗ trợ việc chon số"):
    random_sessions = []

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="random", brief="Lấy số ngẫu nhiên trong 1 khoản cho trước",
                      description="vd: lấy random số từ 1 - 9.  !random 1 9")
    async def random(self, ctx: commands.Context, min, max):
        if min.isnumeric() is False or max.isnumeric() is False:
            await ctx.send("Min hoặc Max phải là số.")
            return

        if int(min) >= int(max):
            await ctx.send("Min phải thấp hơn Max chứ ba...")
            return

        embed = Embed(title="Số ngẫu nhiên:", description=random.randrange(int(min), int(max)))
        await ctx.send(embed=embed)

    @commands.command(name="startexrandom", brief="Khởi tạo 1 phiên random số nhưng không bị trùng",
                      description="VD: random từ 1 tới 10 nhưng mỗi lần random không bị trùng số (để lấy số tiếp theo gõ exrandom): !startexrandom 1 10")
    async def start_exrandom(self, ctx: commands.Context, minimum, maximum):
        author = ctx.author
        index = self.get_author_index(author)
        channel_id = ctx.channel.id
        if index == -1:
            random_model = AdvancedRandomModel(minimum=int(minimum),
                                               maximum=int(maximum),
                                               owner=author,
                                               channel_id=channel_id)
            self.random_sessions.append(random_model)
        else:
            self.random_sessions[index] = AdvancedRandomModel(minimum=int(minimum),
                                                              maximum=int(maximum),
                                                              owner=author,
                                                              channel_id=channel_id)
        await ctx.send(
            "Đã khởi tạo phiên quay số ngẫu nhiên từ `" + minimum + "` đến `" + maximum + "`\nDùng `!exrandom` để bắt đầu")

    @commands.command(name="stopexrandom", brief="Xóa phiên random số trước đó")
    async def stop_exrandom(self, ctx: commands.Context):
        index = self.get_author_index(ctx.author)
        if index != -1:
            self.random_sessions.pop(index)
            await ctx.send("Đã xóa phiên quay số ngẫu nhiên của bạn")
        else:
            await ctx.send("Không thấy phiên quay số, trước đó đã tạo chưa ba?")

    @commands.command(name="exrandom", brief="Bắt đầu quay số theo phiên quay số đã tạo trước đó")
    async def get_random_with_exclude(self, ctx: commands.Context):
        author = ctx.author
        index = self.get_author_index(author)
        if index != -1:
            random_model = self.random_sessions[index]

            if (random_model.maximum - random_model.minimum + 1) == len(random_model.exclude):
                await ctx.send("Đã hết số để quay")
                await self.sort_exclude_random_numbers(ctx)
                await self.stop_exrandom(ctx)
                return

            while True:
                random_number = random.randint(random_model.minimum, random_model.maximum)
                if random_number not in random_model.exclude:
                    random_model.exclude.append(random_number)

                    embed = Embed(title=random_number, description=f"Các số đã ra trước đó: {random_model.exclude}")
                    await ctx.send(embed=embed)

                    return
        else:
            await ctx.send("Không thấy phiên quay số, trước đó đã tạo chưa ba?")

    @commands.command(name="sortexrandom", brief="Sắp xếp lại theo thứ tự tăng dần với các số đã ra trước đó")
    async def sort_exclude_random_numbers(self, ctx: commands.Context):
        author = ctx.author
        index = self.get_author_index(author)
        if index != -1:
            random_model = self.random_sessions[index]
            excludes = random_model.exclude
            excludes.sort()

            embed = Embed(description=f"Các số đã ra trước đó: {random_model.exclude}")
            await ctx.send(embed=embed)

    def get_author_index(self, author):
        for index, random_model in enumerate(self.random_sessions):
            if random_model.owner.id == author.id:
                return index
        return -1


def setup(bot):
    fun_cog = RandomNumberCog(bot)
    bot.add_cog(fun_cog)
