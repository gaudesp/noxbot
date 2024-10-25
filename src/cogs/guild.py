# src/cogs/guild.py
import discord
from discord.ext import commands
from src.services.guild import GuildService
from src.utils.discord import DiscordBot

class GuildCog(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le cog de guilde avec le service de guilde."""
    self.bot = bot
    self.guild_service = GuildService(bot)

  @commands.Cog.listener()
  async def on_guild_join(self, guild: discord.Guild):
    """Événement appelé lorsqu'un serveur (guilde) ajoute le bot."""
    await self.guild_service.add_guild(guild.id, guild.name)
    self.bot.log(f"Guild {guild.name} (ID: {guild.id}) has added {self.bot.settings.bot_name} to its server", "discord.on_guild_join")

  @commands.Cog.listener()
  async def on_guild_remove(self, guild: discord.Guild):
    """Événement appelé lorsqu'un serveur (guilde) retire le bot."""
    await self.guild_service.delete_guild(guild.id)
    self.bot.log(f"Guild {guild.name} (ID: {guild.id}) has removed {self.bot.settings.bot_name} to its server", "discord.on_guild_remove")

async def setup(bot: DiscordBot) -> None:
  """Configure le cog de guilde avec le bot."""
  await bot.add_cog(GuildCog(bot))
