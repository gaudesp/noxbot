# commands/add_game.py
import traceback
import discord
from discord.ext import commands
from discord import app_commands
from repositories import game_repository
from services.steam_service import SteamService
from services.news_service import NewsService
from helpers.autocomplete_helper import game_app_id_autocomplete
from utils.logger import logger

class AddGameCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name='addgame', description='Ajoutez un jeu à suivre')
  @app_commands.autocomplete(game=game_app_id_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def add_game(self, interaction: discord.Interaction, game: str, channel: discord.TextChannel):
    app_id = game
    try:
      existing_game = game_repository.get_game_for_guild(app_id, interaction.guild.id)
      if existing_game:
        await interaction.response.send_message(
          f"Le jeu **{existing_game.game_name}** (`{existing_game.app_id}`) est déjà suivi dans {existing_game.channel}.",
          ephemeral=True
        )
        return
      game_name = await SteamService().get_game_name(app_id)
      if game_name:
        game = game_repository.add_game(app_id=app_id, guild_id=interaction.guild.id, channel_id=channel.id, game_name=game_name)
        await NewsService(self.bot).update_last_news(app_id, interaction.guild.id)
        await interaction.response.send_message(f"Le jeu **{game.game_name}** (`{game.app_id}`) sera désormais suivi dans {game.channel}.", ephemeral=True)
      else:
        await interaction.response.send_message(f"Impossible de trouver un jeu avec l'AppID `{app_id}`.",ephemeral=True)
    except Exception as e:
      logger.log(f"Une erreur est survenue: {str(e)}\n{traceback.format_exc()}", "error")
      await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)
