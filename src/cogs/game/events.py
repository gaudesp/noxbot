from utils.logging import logger
from discord.ext import commands
from utils.discord import DiscordBot

log = logger.get_logger(__name__)

class GameEvents(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self) -> None:
    log.warning('GameEvents on_ready') 

async def setup(bot: DiscordBot) -> None:
  log.warning('GameEvents setup')
  await bot.add_cog(GameEvents(bot))
