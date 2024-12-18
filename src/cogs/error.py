# src/cogs/error.py
import traceback
import discord
from discord.ext import commands
from logging import ERROR, CRITICAL
from src.utils.discord import DiscordBot

class ErrorCog(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le cog d'erreurs avec le bot."""
    self.bot = bot
    self.default_error_message = "Une erreur est survenue."
    bot.tree.error(self.on_app_command_error)

  @commands.Cog.listener()
  async def on_error(self, event, *args, **kwargs) -> None:
    """Gestion des erreurs inattendues dans les événements Discord."""
    self.bot.log(f"Unexpected error in event: {event}, args: {args}, kwargs: {kwargs}", "discord.on_error", CRITICAL)

  @commands.Cog.listener()
  async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
    """Gestion des erreurs pour les commandes classiques."""
    await self._handle_error(ctx, error)

  @commands.Cog.listener()
  async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    """Gestion des erreurs pour les commandes d'application."""
    await self._handle_error(interaction, error)

  async def _handle_error(self, ctx_or_interaction, error: Exception) -> None:
    """Traite les erreurs en journalisant le traceback et en envoyant un message d'erreur."""
    error_traceback = traceback.format_exc()
    self.bot.log(f"Error occurred: {type(error).__name__}: {error}\n{error_traceback}", "discord._handle_error", ERROR)

    if isinstance(ctx_or_interaction, commands.Context):
      await self._send_error_message(ctx_or_interaction, str(error))
    elif isinstance(ctx_or_interaction, discord.Interaction):
      await self._send_error_message(interaction=ctx_or_interaction, message=str(error))

  async def _send_error_message(self, ctx: commands.Context=None, interaction=None, message=None) -> None:
    """Envoie un message d'erreur à l'utilisateur selon le contexte."""
    if ctx:
      try:
        await ctx.send(self.default_error_message, ephemeral=True)
      except discord.errors.Forbidden:
        self.bot.log("Bot does not have permission to send messages in this channel.", "discord._send_error_message", ERROR)
    elif interaction:
      try:
        await interaction.response.send_message(self.default_error_message, ephemeral=True)
      except discord.errors.InteractionResponded:
        self.bot.log("Interaction has already been responded to.", "discord._send_error_message", ERROR)

async def setup(bot: DiscordBot) -> None:
  """Configure le cog d'erreurs avec le bot."""
  await bot.add_cog(ErrorCog(bot))
