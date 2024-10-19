# commands/reset_game.py
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from repositories import game_repository

class ResetGamesCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='resetgames', description='Supprimez tous les jeux suivis du serveur')
  @app_commands.checks.has_permissions(administrator=True)
  async def reset_games(self, interaction: discord.Interaction):
    deleted_games = game_repository.delete_all_games(interaction.guild.id)
    if deleted_games:
      await interaction.response.send_message(f"{deleted_games} jeux ont été supprimés avec succès.", ephemeral=True)
    else:
      await interaction.response.send_message("Aucun jeu à supprimer.", ephemeral=True)

async def setup(bot):
  await bot.add_cog(ResetGamesCommand(bot))
