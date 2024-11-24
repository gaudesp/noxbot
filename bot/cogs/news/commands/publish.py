import discord
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from bot.decorators import ensure_server, ensure_game
from models import FollowedGame, Game
from discord.ext import commands
from discord import app_commands
from utils.discord import DiscordBot, NewsEmbed

class PublishCommands(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot
    self.server = None
    self.game = None

  @app_commands.command(name='nx_publish', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  @ensure_server
  @ensure_game
  async def publish(self, interaction: discord.Interaction, steam_id: str) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)

    if not self.game:
      await interaction.followup.send(f"Le jeu n'existe pas.")
      return
    
    find_followed_game = await self.bot.database.execute(select(FollowedGame).options(joinedload(FollowedGame.game).joinedload(Game.news)).where(FollowedGame.game_id == self.game.id, FollowedGame.server_id == self.server.id))
    followed_game = find_followed_game.scalar_one_or_none()
    if not followed_game:
      await interaction.followup.send(f"Le jeu n'est pas suivi.")
      return
    
    if not followed_game.game.news:
      await interaction.followup.send(f"Aucune actualité n'est disponible pour le jeu {followed_game.game.name}.")
      return
    
    news_embed = NewsEmbed(news=followed_game.game.news.to_dict(), game=followed_game.game.to_dict())
    channel = self.bot.get_channel(int(followed_game.discord_channel_id))
    await channel.send(embed=news_embed.create())
    await interaction.followup.send(f"La dernière actualité du jeu {followed_game.game.name} a été publié dans le channel {followed_game.channel}.")

async def setup(bot: DiscordBot) -> None:
  await bot.add_cog(PublishCommands(bot))
