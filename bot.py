# bot.py
import discord
import logging
from config.settings import Settings
from src.utils.discord import DiscordBot
from src.utils.helper import set_logging

if __name__ == '__main__':
  bot = DiscordBot(intents=discord.Intents.all())
  bot.settings = Settings()
  bot.logger, streamHandler = set_logging(file_level=logging.DEBUG, console_level=logging.INFO)
  bot.run(
    bot.settings.discord_token,
    reconnect=True,
    log_handler=streamHandler,
    log_level=logging.DEBUG,
  )
