# src/cogs/events.py
from discord.ext import commands
from src.events.on_ready import OnReadyEvent

class EventsCogs(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.on_ready_event = OnReadyEvent(bot)

  @commands.Cog.listener()
  async def on_ready(self):
    await self.on_ready_event.on_ready()

async def setup(bot):
  await bot.add_cog(EventsCogs(bot))
