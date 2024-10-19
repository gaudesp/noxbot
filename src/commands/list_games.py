# src/commands/list_game.py
import traceback
import discord
from discord import app_commands
from discord.ext import commands
from src.repositories import game_repository
from src.utils.logger import logger

class ListGamesCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name='listgame', description='Listez les jeux suivis')
  @app_commands.checks.has_permissions(administrator=True)
  async def list_games(self, interaction: discord.Interaction):
    try:
      games = game_repository.get_games_for_guild(guild_id=interaction.guild.id)
      if not games:
        await interaction.response.send_message("Aucun jeu n'est suivi sur ce serveur.", ephemeral=True)
        return
      game_list = '\n'.join([f"**{game.game_name}** (`{game.app_id}`) dans {game.channel}" for game in games])
      await interaction.response.send_message(f"Jeux suivis sur ce serveur:\n{game_list}", ephemeral=True)
    except Exception as e:
      logger.log(f"Une erreur est survenue: {str(e)}\n{traceback.format_exc()}", "error")
      await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)
