# commands/last_news.py
import traceback
import discord
from discord import app_commands
from discord.ext import commands
from repositories import game_repository
from services.news_service import NewsService
from utils.autocomplete import game_name_autocomplete
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
        await NewsService(self.bot).get_last_news(game.app_id, game.guild_id, game.channel_id, game.game_name, game.last_news_id, check_last_news=False)
        await interaction.response.send_message(f"La dernière actualité du jeu **{game.game_name}** a été publiée dans le channel {game.channel}.", ephemeral=True)
      else:
        await interaction.response.send_message(f"Impossible de trouver un jeu avec l'AppID `{app_id}`.", ephemeral=True)
    except Exception as e:
      logger.log(f"Erreur lors de la publication de l'actualité: {str(e)}\n{traceback.format_exc()}", "error")
      await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)
