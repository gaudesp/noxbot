import discord
from utils.logging import logger
from discord.ext import commands
from discord import app_commands
from utils.discord import DiscordBot

log = logger.get_logger(__name__)

class PingCommands(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot

  @app_commands.command(name='nx_ping', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  async def ping(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)
    if interaction.user.id != self.bot.owner_id:
      log.warning('Pong!')
      await interaction.followup.send('Pong!')
    else:
      await interaction.followup.send('Vous n\'êtes pas autorisé à utiliser cette commande.')

async def setup(bot: DiscordBot) -> None:
  await bot.add_cog(PingCommands(bot))
