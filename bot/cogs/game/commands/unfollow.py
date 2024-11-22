import discord
from sqlalchemy.future import select
from bot.decorators.server import ensure_server
from models import Game, FollowedGame, Server
from discord.ext import commands
from discord import app_commands
from utils.discord import DiscordBot

class UnfollowCommands(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot
    self.server = None

  @app_commands.command(name='nx_unfollow', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  @ensure_server
  async def unfollow(self, interaction: discord.Interaction, game_id: str) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)

    find_game = await self.bot.database.execute(select(Game).where(Game.id == game_id))
    game: Game = find_game.scalar_one_or_none()
    if not game:
      await interaction.followup.send(f"Le jeu n'existe pas.")
      return

    find_followed_game = await self.bot.database.execute(select(FollowedGame).where(FollowedGame.game_id == game.id, FollowedGame.server_id == self.server.id))
    followed_game = find_followed_game.scalar_one_or_none()
    if not followed_game:
      await interaction.followup.send(f"{game.name} n'est pas suivi")
      return
  
    followed_game: FollowedGame = await self.bot.database.delete(followed_game)
    await interaction.followup.send(f"{game.name} ne sera plus suivi")

async def setup(bot: DiscordBot) -> None:
  await bot.add_cog(UnfollowCommands(bot))
