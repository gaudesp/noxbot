# events/on_ready.py
from discord.ext import commands
from repositories import game_repository
from tasks.check_for_news import check_for_news
from utils.logger import logger

class OnReadyEvent(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def on_ready(self):
    logger.log(f'{self.bot.user} est prêt et en ligne.')
    await self.sync_commands()
    await self.initialize_db()
    await check_for_news.start(self.bot)

  async def sync_commands(self):
    try:
      synced = await self.bot.tree.sync()
      logger.log(f'{len(synced)} commande(s) synchronisée(s)')
    except Exception as e:
      logger.log(f"Erreur lors de la synchronisation des commandes: {e}", "error")

  async def initialize_db(self):
    game_repository.init_db()
