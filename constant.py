from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN = getenv('DISCORD_BOT_TOKEN')
LOG_CHANNEL_ID = getenv('LOG_CHANNEL_ID', 1077559395426246698)
