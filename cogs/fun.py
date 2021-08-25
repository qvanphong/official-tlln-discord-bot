import random
import re
from inspect import Parameter

import discord
from discord import Embed
from discord.ext import commands, tasks
from checkers import global_checker
from repositories import spammer_repository
from helpers import app_config


class FunCog(commands.Cog, name="Linh tinh", description="Các lệnh linh ta linh tinh"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.remove_spammer_role_on_expire.start()

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
                      brief="Lấy ảnh kích thước lớn của emoji")
    async def emoji(self, ctx, emoji):
        emoji_pattern = r"<a?:\S*:([0-9]*)>"
        match = re.search(emoji_pattern, emoji)

        if match is not None:
            emoji_id = int(match.group(1))
            file_type = "gif" if emoji[1] == "a" else "png"
            await ctx.send(f"https://cdn.discordapp.com/emojis/{emoji_id}.{file_type}")
        else:
            await self.bot.on_command_error(ctx,
                                            commands.errors.MissingRequiredArgument(Parameter(name="emoji",
                                                                                              kind=Parameter.KEYWORD_ONLY)))

    @commands.command(name="dh",
                      brief="Tài liệu Duy Huỳnh")
    async def duy_huynh(self, ctx):
        await ctx.send(">>> Tài liệu mới nhất của Duy Huỳnh:"
                       "https://cdn.discordapp.com/attachments/813452767099355136/859710887387987988"
                       "/DUY_HUYNH_By_Category.pdf")

    @commands.command(name="tailieu",
                      brief="Tài liệu đọc để Trở Lại Làm Người")
    async def tailieu(self, ctx):
        await ctx.send(">>> Tài liệu về Stoic, Carl Jung, Duy Huỳnh, Nguyễn Duy Cần,... trên Trở lại làm người:"
                       "https://www.facebook.com/permalink.php?story_fbid=112580303705418&id=109294147367367")

    @commands.command(name="randomcuck",
                      brief="Random Cục",
                      hidden=True)
    @global_checker.in_channel(app_config.get_config("ark_channel"))
    @commands.check_any(global_checker.is_dev(), commands.has_any_role(857151088687579147, 776478341271781387))
    async def random_cuck(self, ctx: commands.Context):
        role = discord.utils.get(ctx.message.guild.roles, id=app_config.get_config("spammer_role"))
        if role is not None:
            latest_message = await ctx.channel.history(limit=200).flatten()
            member = random.choice(latest_message).author
            await member.add_roles(role)
            spammer_repository.save_spammer(ctx.message.author.id, ctx.message.created_at.timestamp())

            embed = Embed(color=0x0DDEFB, description=f"🎉 🎉 Xin chúc mừng <@!{member.id}>🎉 🎉")
            embed.set_author(name="Spammer Giveaway")

            await ctx.send(embed=embed)

    @tasks.loop(minutes=10)
    async def remove_spammer_role_on_expire(self):
        guild = self.bot.get_guild(app_config.get_config("server_id"))
        if guild is not None:
            role = discord.utils.get(guild.roles, id=app_config.get_config("spammer_role"))
            if role is not None:
                expired_spammers = spammer_repository.get_spammers_expired_time(600)
                for spammer in expired_spammers:
                    member = guild.get_member(spammer['id'])
                    await member.remove_roles(role, reason="Auto remove role (from random spammer)")
                    spammer_repository.remove_spammer(spammer['id'])


def setup(bot):
    fun_cog = FunCog(bot)
    bot.add_cog(fun_cog)
