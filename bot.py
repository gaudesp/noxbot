# bot.py
import discord
from discord.ext import commands
import asyncio

from config import DISCORD_APP_ID, DISCORD_TOKEN
from utils.logger import logger

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents, application_id=DISCORD_APP_ID)

async def load_extensions():
  await bot.load_extension('cogs.commands')
  await bot.load_extension('cogs.events')

async def main():
  await load_extensions()
  await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    asyncio.run(bot.close())
  except Exception as e:
    logger.log(f'Une erreur a été détectée : {e}', 'error')
