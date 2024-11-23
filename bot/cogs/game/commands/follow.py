import discord
from sqlalchemy.future import select
from bot.decorators import ensure_server, ensure_game
from bot.services.news import NewsService
from models import FollowedGame, News
from discord.ext import commands
from discord import app_commands
from utils.discord import DiscordBot
from utils.steamer import steam

class FollowCommands(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot
    self.server = None
    self.game = None
    self.news_service = NewsService(bot.database)

  @app_commands.command(name='nx_follow', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  @ensure_server
  @ensure_game
  async def follow(self, interaction: discord.Interaction, steam_id: str, channel: discord.TextChannel) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)

    if not self.game:
      await interaction.followup.send(f"Le jeu n'existe pas.")
      return

    find_followed_game = await self.bot.database.execute(select(FollowedGame).where(FollowedGame.game_id == self.game.id, FollowedGame.server_id == self.server.id))
    followed_game = find_followed_game.scalar_one_or_none()
    if followed_game:
      await interaction.followup.send(f"{self.game.name} est déjà suivi dans le channel {followed_game.channel}")
      return

    followed_game: FollowedGame = await self.bot.database.insert(FollowedGame(discord_channel_id=channel.id, game_id=self.game.id, server_id=self.server.id))
    await interaction.followup.send(f"Les prochaines actualités de {self.game.name} seront publiées dans le channel {followed_game.channel}")

async def setup(bot: DiscordBot) -> None:
  await bot.add_cog(FollowCommands(bot))
