from discord.ext import commands

from helpers import app_config as _app_config


def from_config_server(ctx):
    return ctx.guild is not None and ctx.guild.id == _app_config.get_config("server_id")


def in_channel(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id

    return commands.check(predicate)


def is_dev():
    def predicate(ctx):
        return ctx.message.author.id == 403040446118363138

    return commands.check(predicate)
