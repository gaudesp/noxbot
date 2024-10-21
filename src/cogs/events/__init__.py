# src/cogs/events/__init__.py
from src.cogs.events.on_ready import OnReadyEvent

async def setup(bot):
  await bot.add_cog(OnReadyEvent(bot))
