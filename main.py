import os
import platform

import discord
from discord.ext import commands, tasks

from helpers import app_config, watcher_config
from tasks.price_watcher import PriceWatcher


intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
intents.guilds = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
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


bot.run(app_config.get_config("token"))
