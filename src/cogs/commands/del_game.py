# src/cogs/commands/del_game.py
import traceback
import discord
from discord import app_commands
from discord.ext import commands
from src.repositories import game_repository
from src.helpers.autocomplete_helper import game_name_autocomplete
from src.utils.logger import logger

class DelGameCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name='delgame', description='Supprimez un jeu suivi')
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def del_game(self, interaction: discord.Interaction, game: str):
    app_id = game
    game = game_repository.delete_game(app_id=app_id, guild_id=interaction.guild.id)
    try:
      if game:
        await interaction.response.send_message(f"Le jeu **{game.game_name}** (`{game.app_id}`) ne sera plus suivi dans {game.channel}.", ephemeral=True)
      else:
        await interaction.response.send_message(f"Aucun jeu avec l'AppID `{app_id}` n'est suivi dans ce serveur.",ephemeral=True)
    except Exception as e:
      logger.log(f"Une erreur est survenue: {str(e)}\n{traceback.format_exc()}", "error")
      await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)
