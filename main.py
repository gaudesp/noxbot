from utils.dotenv import setting
from utils.discord import bot
from utils.logging import logging

if __name__ == "__main__":
  bot.run(setting.get_discord_token())
