# src/cogs/guild.py
import discord
from discord import app_commands
from discord.ext import commands
from src.services.guild import GuildService
from src.utils.discord import DiscordBot

class GuildCog(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le cog de guilde avec le service de guilde."""
    self.bot = bot
    self.bot_name = self.bot.user.name
    self.guild_service = GuildService(bot)

  @commands.Cog.listener()
  async def on_guild_join(self, guild: discord.Guild):
    """Événement appelé lorsqu'un serveur (guilde) ajoute le bot."""
    await self.guild_service.add_guild(guild.id, guild.name)
    self.bot.log(f"Guild {guild.name} (ID: {guild.id}) has added {self.bot_name} to its server", "discord.on_guild_join")

  @commands.Cog.listener()
  async def on_guild_remove(self, guild: discord.Guild):
    """Événement appelé lorsqu'un serveur (guilde) retire le bot."""
    await self.guild_service.delete_guild(guild.id)
    self.bot.log(f"Guild {guild.name} (ID: {guild.id}) has removed {self.bot_name} to its server", "discord.on_guild_remove")

  @app_commands.autocomplete(locale='locale_autocomplete')
  async def locale_autocomplete(self, interaction: discord.Interaction, current: str) -> None:
    """Fournit des suggestions d'autocomplétion pour la locale."""
    await interaction.response.defer(thinking=True)
    matching_locales = self.bot.i18n.get_locales()
    choices = [
      app_commands.Choice(name=locale, value=str(locale))
      for locale in matching_locales if current.lower() in locale.lower()
    ]
    await interaction.response.autocomplete(choices)

  @app_commands.command(name='nx_lang', description='placeholder')
  @app_commands.autocomplete(locale=locale_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def define_locale(self, interaction: discord.Interaction, locale: str) -> None:
    """Met à jour la langue de la guilde uniquement si la locale est valide."""
    if locale not in self.bot.i18n.get_locales():
      await interaction.response.send_message(self.bot.i18n.translate("cogs.guild.commands.nx_lang.messages.not_found", language=locale),ephemeral=True)
      return

    success = await self.guild_service.update_guild_locale(interaction.guild.id, locale)
    if success:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.guild.commands.nx_lang.messages.success", language=locale),ephemeral=True)
    else:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.guild.commands.nx_lang.not_updated"),ephemeral=True)

async def setup(bot: DiscordBot) -> None:
  """Configure le cog de guilde avec le bot."""
  await bot.add_cog(GuildCog(bot))
