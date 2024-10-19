# cogs/commands.py
from discord.ext import commands
from commands.add_game import AddGameCommand
from commands.del_game import DelGameCommand
from commands.list_games import ListGamesCommand
from commands.last_news import LastNewsCommand
from commands.reset_games import ResetGamesCommand

class CommandsCogs(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.tree.add_command(AddGameCommand(bot).add_game)
    self.bot.tree.add_command(DelGameCommand(bot).del_game)
    self.bot.tree.add_command(ListGamesCommand(bot).list_games)
    self.bot.tree.add_command(LastNewsCommand(bot).last_news)
    self.bot.tree.add_command(ResetGamesCommand(bot).reset_games)

async def setup(bot):
  await bot.add_cog(CommandsCogs(bot))
