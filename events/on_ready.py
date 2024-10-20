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
    synced = await self.bot.tree.sync()
    command_names = [command.name for command in synced]
    logger.log(f'{len(synced)} commande(s) synchronisée(s) : {', '.join(command_names)}', "info")

  async def initialize_db(self):
    game_repository.init_db()
    games = {(game.app_id, game.game_name) for game in game_repository.get_all_games()}
    games_info = ', '.join(f'{name} (ID: {app_id})' for app_id, name in games)
    logger.log(f"{len(games)} jeu(x) suivi(s) : {games_info}", "info")
