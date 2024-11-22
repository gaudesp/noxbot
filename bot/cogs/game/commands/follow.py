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

    find_followed_game = await self.bot.database.execute(select(FollowedGame).where(FollowedGame.game_id == self.game.id, FollowedGame.server_id == self.server.id))
    followed_game = find_followed_game.scalar_one_or_none()
    if followed_game:
      await interaction.followup.send(f"{self.game.name} est déjà suivi dans le channel {followed_game.channel}")
      return
    
    steam_news = await self.news_service.get_news_by_steam_id(steam_id)
    if not steam_news:
      await interaction.followup.send(f"Aucune actualité n'est disponible pour le jeu {self.game.name}")
      return
  
    followed_game: FollowedGame = await self.bot.database.insert(FollowedGame(discord_channel_id=channel.id, game_id=self.game.id, server_id=self.server.id))
    find_news = await self.bot.database.execute(select(News).where(News.game_id == self.game.id))
    news = find_news.scalar_one_or_none()
    if not news:
      news = await self.bot.database.insert(News(**steam_news, game_id=self.game.id))

    await interaction.followup.send(f"Les prochaines actualités de {self.game.name} seront désormais publiées dans le channel {followed_game.channel}")

async def setup(bot: DiscordBot) -> None:
  await bot.add_cog(FollowCommands(bot))
