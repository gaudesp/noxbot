# config.py
import os
from dotenv import load_dotenv

load_dotenv()

CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 3600))
DB_PATH = 'db/noxbot.db'
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_APP_ID = os.getenv("DISCORD_APP_ID")
