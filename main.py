import asyncio
import os
import platform
import sys
import traceback

import discord
from discord import Embed
from discord.ext import commands, tasks
from pretty_help import PrettyHelp

from checkers import global_checker
from helpers import app_config, watcher_config
from tasks.cex_gas_balance_watcher import CEXGasBalanceWatcher
from tasks.price_watcher import PriceWatcher

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

initial_cog = [
    "cogs.fun",
    "cogs.price_check",
    "cogs.random_number"
]

bot = commands.Bot(command_prefix='!', intents=intents)

price_watcher: PriceWatcher = None
cexGasBalanceWatcher: CEXGasBalanceWatcher = None

# menu = DefaultMenu('◀️', '▶️', '❌', 10)

bot.help_command = PrettyHelp(
    color=discord.Colour.green(),
    index_title="Danh mục (Categories)",
    no_category="Không có tên danh mục",
    ending_note="Gõ !help command để xem thêm thông tin 1 câu lệnh cụ thể\n"
                "Gõ !help category để xem các lệnh trong danh mục đó",
    show_hidden=False,
    show_index=True)


@bot.event
async def on_ready():
    synced = await bot.tree.sync()

    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print(f"Synced {len(synced)} commands")
    print("-------------------")

    global price_watcher, cexGasBalanceWatcher
    price_watcher = PriceWatcher(bot=bot)
    price_watcher_task.start()

    cexGasBalanceWatcher = CEXGasBalanceWatcher(bot=bot)
    cex_gas_balance_watcher.start()
    await cexGasBalanceWatcher.update_balance(first_init=True)


@tasks.loop(seconds=3600)
async def cex_gas_balance_watcher():
    global cexGasBalanceWatcher
    await cexGasBalanceWatcher.update_balance()


@tasks.loop(seconds=watcher_config.get_config("update_coinbot_interval"))
async def price_watcher_task():
    global price_watcher
    await price_watcher.check_and_update_bot_name()


@bot.check
async def from_config_server(ctx):
    return global_checker.from_config_server(ctx)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        pass
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"Câu lệnh bị thiếu giá trị `<{error.param.name}>` hoặc không hợp lệ, "
                       f"hãy gõ `!help {ctx.invoked_with}` để xem chi tiết")
    elif isinstance(error, commands.errors.ExpectedClosingQuoteError):
        ctx.send(f"Câu lệnh không hợp lệ do thừa dấu \" ở đầu hoặc cuối. "
                 f"Hãy gõ `!help {ctx.invoked_with}` để xem chi tiết")
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@bot.tree.context_menu(name="Bookmark")
async def on_bookmark(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True)
    original_resp = await interaction.original_response()

    dm_ch = interaction.user.dm_channel
    if dm_ch is None:
        dm_ch = await interaction.user.create_dm()

    try:
        [full_msg_content, msg_content, attachment_content, stickers_content] = to_bookmark_content(message)
        if len(full_msg_content) <= 1400:  # if message content size is not reach Discord's limit
            await send_embed_style_bookmark(full_msg_content, message, dm_ch)
        elif len(msg_content) <= 1400:   # if the only message content is not reach Discord's limit, separate it with attachment & sticker
            await send_embed_style_bookmark(msg_content, message, dm_ch, 1, 2)

            attachment_and_sticker_content = attachment_content + stickers_content
            await send_embed_style_bookmark(attachment_and_sticker_content, message, dm_ch, 2, 2)
        else:
            # Split message into small part then send
            await send_embed_style_bookmark("[ Nội dung dài nên sẽ được gửi ở dạng tin nhắn phía dưới, nếu không thấy "
                                            "tin nhắn thì là bug, mà bug thì hú thằng fonk đi 🐔]", message, dm_ch)
            await send_raw_style_bookmark(msg_content, attachment_content, stickers_content, dm_ch)

        await original_resp.edit(content="Đã gửi nội dung bookmark, check in bốc <:Happy:776922281871015966>")
    except discord.Forbidden:
        await original_resp.edit(content="Không gửi được tin nhắn, mở cho phép inbox riêng đi cha nội "
                                         "<:phonglon:872123547865198673>")


@bot.tree.context_menu(name="Unbookmark")
async def on_unbookmark(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True)
    original_resp = await interaction.original_response()

    if message.author.id == bot.user.id:
        await message.delete()
        await original_resp.edit(content="✅ Đã xoá bookmark")
    else:
        await original_resp.edit(content="❌ Chỉ dùng chức năng này trên chính tin nhắn của bot trong inbox")


def to_bookmark_content(message: discord.Message):
    msg_content = message.content
    full_msg_content = message.content + "\n"
    attachment_content = ''
    stickers_content = ''

    if len(message.attachments) > 0:
        for attachment in message.attachments:
            attachment_content += "[Attachment] " + attachment.url + "\n"
            full_msg_content += "[Attachment] " + attachment.url + "\n"

    if len(message.stickers) > 0:
        for sticker in message.stickers:
            stickers_content += "[Image] " + sticker.url + "\n"
            full_msg_content += "[Image] " + sticker.url + "\n"

    return [full_msg_content, msg_content, attachment_content, stickers_content]


async def send_embed_style_bookmark(msg_content,
                                    message: discord.Message,
                                    dm_channel,
                                    bookmark_part=None,
                                    total_bookmark_part=None):
    guild_id = message.channel.guild.id
    channel_id = message.channel.id
    msg_id = message.id
    author_id = message.author.id

    part = f"{bookmark_part}/{total_bookmark_part}" if bookmark_part is not None and total_bookmark_part is not None else ""
    title = f"Bookmark 🔖 {part}"

    embed = Embed(color=0x0DDEFB, title=title)
    embed.add_field(name="Tin nhắn", value=f"https://discord.com/channels/{guild_id}/{channel_id}/{msg_id}")
    embed.add_field(name="Tác giả", value=f"<@!{author_id}>")
    embed.add_field(name="Nội dung", value=msg_content, inline=False)

    await dm_channel.send(embed=embed)


async def send_raw_style_bookmark(msg_content: str,
                                  attachment_content: str,
                                  stickers_content: str,
                                  dm_channel):
    max_msg_part_character = 1400

    from_index = 0
    to_index = max_msg_part_character  # max character to split into parts

    msg_parts = []

    anti_loop = 10
    loop_time = 0

    while True:
        part = msg_content[from_index:to_index]

        if to_index >= len(msg_content):
            msg_parts.append(part)
            break
        else:
            try:
                last_space_index = part.rindex(" ")
                from_index = last_space_index
                to_index = from_index + max_msg_part_character

                part = part[0:last_space_index]
            except ValueError:
                # no space character
                from_index = to_index
                to_index = from_index + max_msg_part_character

            msg_parts.append(part)

        loop_time += 1
        if loop_time >= anti_loop:
            break

    for index, msg_part in enumerate(msg_parts):
        await dm_channel.send(msg_part)

    if len(attachment_content) > 0 or len(stickers_content) > 0:
        await dm_channel.send(attachment_content + stickers_content)

async def main():
    async with bot:
        for cog in initial_cog:
            await bot.load_extension(cog)
        await bot.start(app_config.get_config("token"))


asyncio.run(main())
