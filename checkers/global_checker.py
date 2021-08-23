from helpers import app_config as _app_config


def from_config_server(ctx):
    return ctx.guild is not None and ctx.guild.id == _app_config.get_config("server_id")
