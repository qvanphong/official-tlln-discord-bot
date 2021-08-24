import random
import re
from inspect import Parameter

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

    @commands.command(name="ava",
                      brief="Lấy avatar của người được tag",
                      description="VD: !ava @Phong")
    async def avatar(self, ctx, user):
        # Normal string, no user tagged
        if "<@" not in user:
            await self.bot.on_command_error(ctx,
                                            commands.errors.MissingRequiredArgument(Parameter(name="user",
                                                                                              kind=Parameter.KEYWORD_ONLY)))
            return
        if len(ctx.message.mentions) == 0:
            await ctx.send("`Không tìm thấy người được tag`")
        else:
            user_tagged = ctx.message.mentions[0]
            avatar = user_tagged.avatar_url

            await ctx.send(avatar)

    @commands.command(name="e",
                      brief="Lấy ảnh kích của emoji")
    async def emoji(self, ctx, emoji):
        emoji_pattern = r"<@?:\S*:([0-9]*)>"
        match = re.search(emoji_pattern, emoji)

        if match is not None:
            emoji_id = int(match.group(1))
            file_type = "gif" if emoji[1] == "@" else "png"
            await ctx.send(f"https://cdn.discordapp.com/emojis/{emoji_id}.{file_type}")


def setup(bot):
    bot.add_cog(FunCog(bot))
