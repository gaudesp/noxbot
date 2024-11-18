from utils.logging import logger
from discord.ext import commands
from utils.discord import DiscordBot

log = logger.get_logger(__name__)

class PingCommands(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot

  @commands.command(name='ping', description='placeholder')
  @commands.has_permissions(administrator=True)
  async def ping(self, ctx: commands.Context) -> None:
    log.warning('Pong!') 
    await ctx.send('Pong!')

async def setup(bot: DiscordBot) -> None:
  log.warning('PingCommands setup')
  await bot.add_cog(PingCommands(bot))
