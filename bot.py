# bot.py
import discord
import logging
from utils.discord_bot import DiscordBot
from utils.logging import set_logging

if __name__ == '__main__':
  bot = DiscordBot(intents=discord.Intents.all())
  bot.logger, streamHandler = set_logging(file_level=logging.DEBUG, console_level=logging.INFO)
  bot.run(
    bot.config["DISCORD_TOKEN"],
    reconnect=True,
    log_handler=streamHandler,
    log_level=logging.DEBUG,
  )
