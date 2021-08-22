from helpers import watcher as watcher
from helpers import app_config as app
from enum import Enum


class PriceStatus(Enum):
    PUMP = 1
    DUMP = -1
    NOTHING = 0


coin_bots_info = {
    'NEO': {'channel': app.get_config("neo_channel"),
            'image': watcher.get_config("neo_image_url"),
            'bot_id': watcher.get_config("neo_bot_id")},

    'GAS': {'channel': app.get_config("neo_channel"),
            'image': watcher.get_config("gas_image_url"),
            'bot_id': watcher.get_config("gas_bot_id")},

    'FIRO': {'channel': app.get_config("firo_channel"),
             'image': watcher.get_config("firo_image_url"),
             'bot_id': watcher.get_config("firo_bot_id")},

    'BTC': {'channel': app.get_config("btc_channel"),
            'image': watcher.get_config("btc_image_url"),
            'bot_id': watcher.get_config("btc_bot_id")},

    'ZEN': {'channel': app.get_config("zen_channel"),
            'image': watcher.get_config("zen_image_url"),
            'bot_id': watcher.get_config("zen_bot_id")},

    'DASH': {'channel': app.get_config("dash_channel"),
             'image': watcher.get_config("dash_image_url"),
             'bot_id': watcher.get_config("dash_bot_id")},

    'ARK': {'channel': app.get_config("ark_channel"),
            'image': watcher.get_config("ark_image_url"),
            'bot_id': watcher.get_config("ark_bot_id")},

    'ETH': {'channel': None,
            'image': watcher.get_config("eth_image_url"),
            'bot_id': watcher.get_config("eth_bot_id")},
}


def get_channel_id(coin_name):
    return coin_bots_info[coin_name]['channel']


def get_coin_image(coin_name):
    return coin_bots_info[coin_name]['image']


def get_bot_id(coin_name):
    return coin_bots_info[coin_name]['bot_id']


def get_ember_color(price_status: PriceStatus):
    if price_status == PriceStatus.PUMP:
        return 0x07F79B
    return 0xE1221D


def get_pump_dump_icon(price_status: PriceStatus):
    if price_status == PriceStatus.PUMP:
        return watcher.get_config("pump_icon")
    return watcher.get_config("dump_icon")
