import os
from dotenv import load_dotenv

load_dotenv()

class Setting:
  def __init__(self):
    self.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    self.SCRAPPEY_TOKEN = os.getenv("SCRAPPEY_TOKEN")
    self.BOT_ENV = os.getenv("BOT_ENV")
