from typing import Any, Optional
import discord
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from bot.decorators import ensure_server, ensure_game
from models import FollowedGame, Server
from discord.ext import commands
from discord import app_commands
from utils.discord import DiscordBot

class TrackedCommands(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot
    self.server = None

  @app_commands.command(name='nx_list', description='Lister les jeux suivis')
  @app_commands.checks.has_permissions(administrator=True)
  @ensure_server
  async def tracked(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)

    find_followed_games = await self.bot.database.execute(select(FollowedGame).options(joinedload(FollowedGame.game)).where(FollowedGame.server_id == self.server.id))
    followed_games = find_followed_games.scalars().all()
    if not followed_games:
      await interaction.followup.send(f"Aucun jeu n'est suivi.")
      return

    game_names = [f"\n- **{followed_game.game.name}** (`{followed_game.game.steam_id}`) ➜ {followed_game.channel}" for followed_game in followed_games]
    games_list = "".join(game_names)

    await interaction.followup.send(f"{len(game_names)} jeu(x) suivi(s) : {games_list}")

async def setup(bot: DiscordBot) -> None:
  await bot.add_cog(TrackedCommands(bot))
