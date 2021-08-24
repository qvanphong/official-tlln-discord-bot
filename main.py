import os
import platform
import sys
import traceback

import discord
from discord.ext import commands, tasks

from checkers import global_checker
from cogs import price_check
from helpers import app_config, watcher_config
from tasks.price_watcher import PriceWatcher

intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
intents.guilds = True
intents.messages = True

initial_cog = [
    "cogs.fun",
    "cogs.price_check"
]

bot = commands.Bot(command_prefix='!', intents=intents)

for cog in initial_cog:
    bot.load_extension(cog)

price_watcher: PriceWatcher = None


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")

    global price_watcher
    price_watcher = PriceWatcher(bot=bot)
    price_watcher_task.start()


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
        await ctx.send(f"Câu lệnh vừa nhập không hợp lệ, hãy gõ `!help {ctx.invoked_with}` để xem chi tiết")
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


bot.run(app_config.get_config("token"))
