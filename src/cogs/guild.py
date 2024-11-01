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

  async def guild_locale_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Fournit des suggestions d'autocomplétion pour la locale."""
    await interaction.response.defer(thinking=True)
    locales = self.bot.i18n.get_locales()
    return [
      app_commands.Choice(name=locale, value=str(locale))
      for locale in locales if current.lower() in locale.lower()
    ][:25] if locales else []

  @app_commands.command(name='nx_lang', description='placeholder')
  @app_commands.autocomplete(locale=guild_locale_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def define_locale(self, interaction: discord.Interaction, locale: str) -> None:
    """Met à jour la langue de la guilde uniquement si la locale est valide."""
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild_id = interaction.guild.id
    guild_locale = await self.guild_service.find_guild_locale(guild_id)
    if locale not in self.bot.i18n.get_locales():
      await interaction.followup.send(self.bot.i18n.translate("cogs.guild.commands.nx_lang.messages.not_found", guild_locale, language=locale))
      return

    success = await self.guild_service.update_guild_locale(interaction.guild, locale)
    if success:
      await interaction.followup.send(self.bot.i18n.translate("cogs.guild.commands.nx_lang.messages.success", locale, language=locale))
    else:
      await interaction.followup.send(self.bot.i18n.translate("cogs.guild.commands.nx_lang.not_updated", locale))

async def setup(bot: DiscordBot) -> None:
  """Configure le cog de guilde avec le bot."""
  await bot.add_cog(GuildCog(bot))
