# src/repositories/game_repository.py
from sqlalchemy import update, delete
from sqlalchemy.future import select
from src.models.game import Game as GameModel
from src.utils.discord import DiscordBot

class GameRepository:
  def __init__(self, bot: DiscordBot):
    self.bot = bot

  async def add_game(self, app_id, guild_id, channel_id, game_name):
    game = GameModel(app_id=app_id, guild_id=guild_id, channel_id=channel_id, game_name=game_name)
    return await self.bot.database.insert(game)

  async def get_all_games(self):
    games = await self.bot.database.execute(select(GameModel))
    return games.scalars().all()
  
  async def get_game_for_guild(self, app_id, guild_id):
    game = await self.bot.database.execute(select(GameModel).where(GameModel.app_id == app_id, GameModel.guild_id == guild_id))
    return game.scalar_one_or_none()
  
  async def get_games_for_guild(self, guild_id):
    games = await self.bot.database.execute(select(GameModel).where(GameModel.guild_id == guild_id))
    return games.scalars().all()

  async def update_last_news_id(self, app_id, guild_id, news_id):
    game = await self.get_game_for_guild(app_id, guild_id)
    if game:
      await self.bot.database.execute(update(GameModel).where(GameModel.app_id == app_id, GameModel.guild_id == guild_id).values(last_news_id=news_id))
      return True
    return False

  async def delete_game(self, app_id, guild_id):
    game = await self.get_game_for_guild(app_id, guild_id)
    if game:
      await self.bot.database.execute(delete(GameModel).where(GameModel.app_id == app_id, GameModel.guild_id == guild_id))
      return game
    return False

  async def delete_all_games(self, guild_id):
    games = await self.get_games_for_guild(guild_id)
    count_deleted = len(games)
    if count_deleted > 0:
      await self.bot.database.execute(delete(GameModel).where(GameModel.guild_id == guild_id))
    return count_deleted
