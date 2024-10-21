# src/cogs/commands/__init__.py
from src.cogs.commands.add_game import AddGameCommand
from src.cogs.commands.del_game import DelGameCommand
from src.cogs.commands.list_games import ListGamesCommand
from src.cogs.commands.last_news import LastNewsCommand
from src.cogs.commands.reset_games import ResetGamesCommand

async def setup(bot):
  await bot.add_cog(AddGameCommand(bot))
  await bot.add_cog(DelGameCommand(bot))
  await bot.add_cog(ListGamesCommand(bot))
  await bot.add_cog(LastNewsCommand(bot))
  await bot.add_cog(ResetGamesCommand(bot))
