import asyncio
import os
import platform
import sys
import traceback

import discord
from discord.ext import commands, tasks
from pretty_help import PrettyHelp, DefaultMenu

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

menu = DefaultMenu('◀️', '▶️', '❌', 10)

bot.help_command = PrettyHelp(navigation=menu,
                              color=discord.Colour.green(),
                              index_title="Danh mục (Categories)",
                              no_category="Không có tên danh mục",
                              ending_note="Gõ !help command để xem thêm thông tin 1 câu lệnh cụ thể\n"
                                          "Gõ !help category để xem các lệnh trong danh mục đó",
                              show_hidden=False,
                              show_index=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")

    global price_watcher, cexGasBalanceWatcher
    price_watcher = PriceWatcher(bot=bot)
    price_watcher_task.start()

    cexGasBalanceWatcher = CEXGasBalanceWatcher(bot=bot)
    cex_gas_balance_watcher.start()
    await cexGasBalanceWatcher.update_balance(first_init=True)

@tasks.loop(hours=1)
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


async def main():
    async with bot:
        for cog in initial_cog:
            await bot.load_extension(cog)
        await bot.start(app_config.get_config("token"))


asyncio.run(main())
