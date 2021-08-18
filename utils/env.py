import os
from dotenv import load_dotenv
import definition

dotenv_path = definition.get_path('.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("Token")
CMC_KEY = os.environ.get("CMCKey")
SERVER_ID = int(os.environ.get("ServerId"))
BINANCE_WS_URL = os.environ.get("BinanceWssURL")

NEO_CHANNEL = int(os.environ.get("NeoChannel"))
ARK_CHANNEL = int(os.environ.get("ArkChannel"))
FIRO_CHANNEL = int(os.environ.get("FiroChannel"))
ZEN_CHANNEL = int(os.environ.get("ZenChannel"))
BTC_CHANNEL = int(os.environ.get("BitcoinChannel"))
DASH_CHANNEL = int(os.environ.get("DashChannel"))
SPAM_BOT_CHANNEL = int(os.environ.get("SpamBotChannel"))

NEO_IMAGE_URL = os.environ.get("NeoImageURL")
GAS_IMAGE_URL = os.environ.get("GasImageURL")
ARK_IMAGE_URL = os.environ.get("ArkImageURL")
FIRO_IMAGE_URL = os.environ.get("FiroImageURL")
ZEN_IMAGE_URL = os.environ.get("ZenImageURL")
BTC_IMAGE_URL = os.environ.get("BitcoinImageURL")
DASH_IMAGE_URL = os.environ.get("DashImageURL")

NEO_BOT_ID = int(os.environ.get("NeoBotID"))
GAS_BOT_ID = int(os.environ.get("GasBotID"))
ARK_BOT_ID = int(os.environ.get("ArkBotID"))
FIRO_BOT_ID = int(os.environ.get("FiroBotID"))
ZEN_BOT_ID = int(os.environ.get("ZenBotID"))
BTC_BOT_ID = int(os.environ.get("BitcoinBotID"))
DASH_BOT_ID = int(os.environ.get("DashBotID"))

PUMP_ICON = os.environ.get("PUMP_ICON")
DUMP_ICON = os.environ.get("DUMP_ICON")
