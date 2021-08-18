import discord
from discord.ext import commands

from utils import env
from utils.price_alert import PriceAlert

intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
intents.guilds = True
intents.messages = True
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    price_alert = PriceAlert(bot)
    bot.loop.create_task(price_alert.start())
    print('Started price alert')


bot.run(env.TOKEN)
