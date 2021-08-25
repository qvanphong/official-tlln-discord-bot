import functools

import discord
from discord.ext import commands
from discord.ext.commands import NoPrivateMessage, MissingAnyRole

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


def is_mod():
    def predicate(ctx):
        mod_roles = [857151088687579147, 776478341271781387, 776373412737974272]
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            raise NoPrivateMessage()

        getter = functools.partial(discord.utils.get, ctx.author.roles)
        if any(getter(id=item) is not None if isinstance(item, int) else getter(name=item) is not None for item in mod_roles):
            return True
        raise MissingAnyRole(mod_roles)

    return commands.check(predicate)
