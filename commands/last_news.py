# commands/last_news.py
import traceback
import discord
from discord import app_commands
from discord.ext import commands
from repositories import game_repository
from services.news_service import NewsService
from helpers.autocomplete_helper import game_name_autocomplete
from utils.logger import logger

class LastNewsCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='lastnews', description="Postez la dernière actualité d'un jeu dans son channel (pour tester)")
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def last_news(self, interaction: discord.Interaction, game: str):
    app_id = game
    try:
      game = game_repository.get_game_for_guild(app_id, interaction.guild.id)
      if game:
        news = await NewsService(self.bot).get_last_news(game)
        if news:
          await interaction.response.send_message(f"La dernière actualité du jeu **{game.game_name}** a été publiée dans le channel {game.channel}.", ephemeral=True)
        else:
          await interaction.response.send_message(f"Aucune nouvelle actualité n'a été trouvée pour le jeu **{game.game_name}**.", ephemeral=True)
      else:
        await interaction.response.send_message(f"Impossible de trouver un jeu avec l'AppID `{app_id}`.", ephemeral=True)
    except Exception as e:
      logger.log(f"Une erreur est survenue: {str(e)}\n{traceback.format_exc()}", "error")
      await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)
