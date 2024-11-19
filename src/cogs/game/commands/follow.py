import discord
from sqlalchemy.future import select
from models import Game, FollowedGame, Server
from utils.logging import logger
from discord.ext import commands
from discord import app_commands
from utils.discord import DiscordBot
from utils.steamer import steam

log = logger.get_logger(__name__)

class FollowCommands(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot

  @app_commands.command(name='nx_follow', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  async def follow(self, interaction: discord.Interaction, steam_id: str, channel: discord.TextChannel) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)

    steam_game = await steam.get_game_info(steam_id)
    if not steam_game:
      await interaction.followup.send(f"Le jeu est introuvable sur Steam.")
      return

    find_game = await self.bot.database.execute(select(Game).where(Game.steam_id == steam_id))
    game = find_game.scalar_one_or_none()
    if not game:
      game: Game = await self.bot.database.insert(Game(name=steam_game.get('name'), steam_id=steam_id))

    find_server = await self.bot.database.execute(select(Server).where(Server.discord_id == interaction.guild.id))
    server = find_server.scalar_one_or_none()
    if not server:
      server: Server = await self.bot.database.insert(Server(name=interaction.guild.name, discord_id=interaction.guild.id))

    find_followed_game = await self.bot.database.execute(select(FollowedGame).where(FollowedGame.game_id == game.id, FollowedGame.server_id == server.id))
    followed_game = find_followed_game.scalar_one_or_none()
    if followed_game:
      await interaction.followup.send(f"{game.name} est déjà suivi dans le channel {followed_game.channel}")
      return
  
    followed_game: FollowedGame = await self.bot.database.insert(FollowedGame(discord_channel_id=channel.id, game_id=game.id, server_id=server.id))
    await interaction.followup.send(f"{game.name} sera désormais suivi dans le channel {followed_game.channel}")

async def setup(bot: DiscordBot) -> None:
  await bot.add_cog(FollowCommands(bot))
