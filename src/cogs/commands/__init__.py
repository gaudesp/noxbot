# src/cogs/commands/__init__.py
from discord.ext import commands as cmd
from src.cogs.commands.add_game import AddGameCommand
from src.cogs.commands.del_game import DelGameCommand
from src.cogs.commands.list_games import ListGamesCommand
from src.cogs.commands.last_news import LastNewsCommand
from src.cogs.commands.reset_games import ResetGamesCommand

class CommandsCogs(cmd.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.tree.add_command(AddGameCommand(bot).add_game)
    self.bot.tree.add_command(DelGameCommand(bot).del_game)
    self.bot.tree.add_command(ListGamesCommand(bot).list_games)
    self.bot.tree.add_command(LastNewsCommand(bot).last_news)
    self.bot.tree.add_command(ResetGamesCommand(bot).reset_games)

async def setup(bot):
  await bot.add_cog(CommandsCogs(bot))
