import random
import re
from inspect import Parameter

import discord
from discord import Embed
from discord.ext import commands, tasks
from checkers import global_checker
from repositories import spammer_repository
from helpers import app_config, fun_cog_helper
import asyncio

class FunCog(commands.Cog, name="Linh tinh", description="Các lệnh linh ta linh tinh"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.remove_spammer_role_on_expire.start()

    @commands.command(name="pick", brief="Chọn ngẫu nhiên các giá trị nhập vào",
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
            avatar = user_tagged.avatar

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

    @commands.command(name="dh", brief="Tài liệu Duy Huỳnh")
    async def duy_huynh(self, ctx):
        await ctx.send(">>> Tài liệu mới nhất của Duy Huỳnh:"
                       "https://cdn.discordapp.com/attachments/813452767099355136/859710887387987988"
                       "/DUY_HUYNH_By_Category.pdf")

    @commands.command(name="tailieu", brief="Tài liệu đọc để Trở Lại Làm Người")
    async def tailieu(self, ctx):
        await ctx.send(">>> Tài liệu về Stoic, Carl Jung, Duy Huỳnh, Nguyễn Duy Cần,... trên Trở lại làm người:"
                       "https://www.facebook.com/permalink.php?story_fbid=112580303705418&id=109294147367367")

    @commands.command(name="randomcuck", brief="Random Cục", hidden=True)
    @commands.check_any(global_checker.is_dev(), global_checker.is_mod())
    async def random_cuck(self, ctx: commands.Context, amount=1):
        if amount > 10:
            await ctx.send(
                f"vl <@!{ctx.message.author.id}>! Ông định giết cả box này à <:angry:776921998999027733><:sung:827892224851312651>")
            return

        role = discord.utils.get(ctx.message.guild.roles, id=app_config.get_config("spammer_role"))
        if role is not None:
            users = []
            selected_members = []

            # Add user to list.
            async for message in ctx.channel.history(limit=200):
                if message.author != ctx.bot.user and message not in users:
                    users.append(message.author)

            if len(users) <= amount:
                selected_members = users
            else:
                for i in range(amount):
                    selected_member = random.choice(users)
                    while selected_member in selected_members:
                        selected_member = random.choice(users)

                    selected_members.append(selected_member)
                    users.remove(selected_member)

            cuc_members_str = ""
            # Random minutes from 10 ~ 30
            period_time = random.randint(app_config.get_config("min_spammer_role_period"),
                                         app_config.get_config("max_spammer_role_period"))

            for member in selected_members:
                spammer_repository.save_spammer(member.id, ctx.message.created_at.timestamp(), period_time)
                cuc_members_str += f"<@!{member.id}> "
                await member.add_roles(role)

            embed = Embed(color=0x0DDEFB,
                          description=f"🎉 🎉 Mày hả bưởi? Đi cai nghiện ngay! 🎉 🎉\n{cuc_members_str}")
            embed.set_author(name="Spammer Role Giveaway")
            embed.add_field(name="Thời gian cai nghiện", value=f"{period_time} phút")
            embed.add_field(name="Người tặng vé cai nghiện", value=f"<@!{ctx.message.author.id}>")

            await ctx.send(embed=embed)

    @commands.command(name="removerandomcuck", brief="Xóa những member bị dính random Cục", hidden=True)
    @commands.check_any(global_checker.is_dev(), global_checker.is_mod())
    async def remove_randomcuck(self, ctx):
        guild = ctx.bot.get_guild(app_config.get_config("server_id"))
        if guild is not None:
            role = discord.utils.get(guild.roles, id=app_config.get_config("spammer_role"))
            if role is not None:
                spammers = spammer_repository.get_all()
                for spammer in spammers:
                    member = guild.get_member(spammer['id'])
                    await member.remove_roles(role,
                                              reason="Auto remove role (from random spammer from !removerandomcuck)")

                    print(f"Removed role for {member.name}")

                    spammer_repository.remove_spammer(spammer['id'])

    @commands.command(name="poll", brief="Tạo một cuộc bình chọn ý kiến",
                      description="!poll <câu hỏi> <lựa chọn A>  <lựa chọn C>  <lựa chọn B>... (Tối đa 10 lựa chọn).\n"
                                  "VD: !poll \"ARK lên bao nhiêu cuối cycle\" \"30$\" \"10$\"")
    async def pool(self, ctx, question, *options):
        if len(options) < 2:
            await self.bot.on_command_error(ctx,
                                            commands.errors.MissingRequiredArgument(
                                                Parameter(name="options",
                                                          kind=Parameter.KEYWORD_ONLY)))
            return

        if len(options) > 10:
            await ctx.send("Hỗ trợ tối đa 10 lựa chọn thôi, nên bớt lại ik <:nhutnhat:776923082064527370>")
            return

        # Delete using command message.
        await ctx.message.delete()

        reaction_emojis = []

        question_title = f"📊 **{question} ❓**"
        options_text = ""

        # Append string to options_text to send options in message.
        for index, option in enumerate(options):
            options_text += f"{fun_cog_helper.regional_emoji[index]}. {option}\n"
            reaction_emojis.append(fun_cog_helper.regional_emoji[index])

        embed = Embed(color=0x0DDEFB, title=question_title, description=options_text)
        embed.set_author(name=f"Cuộc thăm dò ý kiến.", icon_url=ctx.message.author.avatar_url)
        sent_poll_message = await ctx.send(embed=embed)

        # Add Reaction
        for emoji in reaction_emojis:
            await sent_poll_message.add_reaction(emoji)

    @commands.command(name="fakecoingiveaway")
    async def fake_coingiveaway(self, ctx):
        await ctx.message.delete()

        author = ctx.message.author
        embed = Embed(title=f"{author.name} has set up a Coin Giveaway!",
                      description='Click the 💰 Reaction below to receive **1 Ѧ**\n'
                                  'The Giveaway is limited to **1** Users so be quick!')
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.add_field(name="Remaining Users", value="**1**", inline=True)
        embed.add_field(name="Remaining Time", value="**5:00** Minutes", inline=True)
        embed.add_field(name="Lucky Users", value="None yet!", inline=False)
        message = await ctx.send(embed=embed)
        await message.add_reaction('💰')

    @commands.command(name="t", hidden=True)
    @commands.check_any(global_checker.is_dev(), global_checker.is_mod())
    async def anonymous_message(self, ctx, channel, *, text):
        channel_id = int(channel.replace("<#", "").replace(">", ""))
        await ctx.message.delete()
        await self.bot \
            .get_guild(app_config.get_config("server_id")) \
            .get_channel(channel_id) \
            .send(text)

    @commands.command(name="xoibac", hidden=True)
    async def xoibac(self, ctx):
        items = ["Pill", "Nứa", "Fancao", "Đức Mèo", "Hương", "Việt Mẽo"]
        selected = []
        for i in range(3):
            random_selected = items[random.randint(0, len(items) - 1)]
            selected.append(random_selected)

            embed = Embed(title=f"Kết quả xới bạc lần {i + 1}", description=random_selected)
            await ctx.send(embed=embed)

            await asyncio.sleep(5 if i != 2 else 0)


        embed = Embed(title="Kết quả xới bạc", description='\n'.join(selected))
        await ctx.send(embed=embed)

    @tasks.loop(minutes=1)
    async def remove_spammer_role_on_expire(self):
        guild = self.bot.get_guild(app_config.get_config("server_id"))
        if guild is not None:
            role = discord.utils.get(guild.roles, id=app_config.get_config("spammer_role"))
            if role is not None:
                expired_spammers = spammer_repository.get_expired_spammer()
                for spammer in expired_spammers:
                    member = guild.get_member(spammer['id'])
                    await member.remove_roles(role, reason="Auto remove role (from random spammer)")

                    print(f"Removed role for {member.name}")

                    spammer_repository.remove_spammer(spammer['id'])


async def setup(bot):
    fun_cog = FunCog(bot)
    await bot.add_cog(fun_cog)
