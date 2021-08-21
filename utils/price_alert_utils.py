import utils.env as env
from enum import Enum


class PriceStatus(Enum):
    PUMP = 1
    DUMP = -1
    NOTHING = 0


data = {
    'neo': {'channel': env.NEO_CHANNEL, 'image': env.NEO_IMAGE_URL, 'bot_id': env.NEO_BOT_ID},
    'gas': {'channel': env.NEO_CHANNEL, 'image': env.GAS_IMAGE_URL, 'bot_id': env.GAS_BOT_ID},
    'firo': {'channel': env.FIRO_CHANNEL, 'image': env.FIRO_IMAGE_URL, 'bot_id': env.FIRO_BOT_ID},
    'btc': {'channel': env.BTC_CHANNEL, 'image': env.BTC_IMAGE_URL, 'bot_id': env.BTC_BOT_ID},
    'zen': {'channel': env.ZEN_CHANNEL, 'image': env.ZEN_IMAGE_URL, 'bot_id': env.ZEN_BOT_ID},
    'dash': {'channel': env.DASH_CHANNEL, 'image': env.DASH_IMAGE_URL, 'bot_id': env.DASH_BOT_ID},
    'ark': {'channel': env.ARK_CHANNEL, 'image': env.ARK_IMAGE_URL, 'bot_id': env.ARK_BOT_ID},
    'eth': {'channel': env.ARK_CHANNEL, 'image': env.ETH_IMAGE_URL, 'bot_id': env.ETH_BOT_ID},
}


def get_channel_id(coin_name):
    return data[coin_name]['channel']


def get_coin_image(coin_name):
    return data[coin_name]['image']


def get_bot_id(coin_name):
    return data[coin_name]['bot_id']


def get_ember_color(price_status: PriceStatus):
    if price_status == PriceStatus.PUMP:
        return 0x07F79B
    return 0xE1221D


def get_pump_dump_icon(price_status: PriceStatus):
    if price_status == PriceStatus.PUMP:
        return env.PUMP_ICON
    return env.DUMP_ICON
