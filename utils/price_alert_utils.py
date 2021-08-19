import utils.env as env


def get_channel_id(coin_name):
    name = coin_name.lower()

    if name == 'neo':
        return env.NEO_CHANNEL
    if name == 'gas':
        return env.NEO_CHANNEL
    if name == 'firo':
        return env.FIRO_CHANNEL
    if name == 'btc':
        return env.BTC_CHANNEL
    if name == 'zen':
        return env.ZEN_CHANNEL
    if name == 'dash':
        return env.DASH_CHANNEL
    if name == 'ark':
        return env.ARK_CHANNEL
    if name == 'gas':
        return env.NEO_CHANNEL


def get_coin_image(coin_name):
    name = coin_name.lower()

    if name == 'neo':
        return env.NEO_IMAGE_URL
    if name == 'gas':
        return env.GAS_IMAGE_URL
    if name == 'firo':
        return env.FIRO_IMAGE_URL
    if name == 'btc':
        return env.BTC_IMAGE_URL
    if name == 'zen':
        return env.ZEN_IMAGE_URL
    if name == 'dash':
        return env.DASH_IMAGE_URL
    if name == 'ark':
        return env.ARK_IMAGE_URL
    if name == 'gas':
        return env.NEO_IMAGE_URL

def get_bot_id(coin_name):
    name = coin_name.lower()

    if name == 'neo':
        return env.NEO_BOT_ID
    if name == 'gas':
        return env.GAS_BOT_ID
    if name == 'firo':
        return env.FIRO_BOT_ID
    if name == 'btc':
        return env.BTC_BOT_ID
    if name == 'zen':
        return env.ZEN_BOT_ID
    if name == 'dash':
        return env.DASH_BOT_ID
    if name == 'ark':
        return env.ARK_BOT_ID
    if name == 'gas':
        return env.NEO_BOT_ID


def get_ember_color(price_change_result):
    if price_change_result == 1:
        return 0x07F79B
    return 0xE1221D


def get_pump_dump_icon(price_change_result):
    if price_change_result == 1:
        return env.PUMP_ICON
    return env.DUMP_ICON
