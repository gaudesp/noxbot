from functools import wraps
import discord
from sqlalchemy.future import select
from models import Game, News
from utils.steamer import steam

def ensure_game(func):
  @wraps(func)
  async def wrapper(self, interaction: discord.Interaction, steam_id, *args, **kwargs):
    find_game = await self.bot.database.execute(select(Game).where(Game.steam_id == steam_id))
    game = find_game.scalar_one_or_none()
    if not game:
      self.game = None

    self.game = game
    return await func(self, interaction, steam_id, *args, **kwargs)
  
  return wrapper

def ensure_steam_game(func):
  @wraps(func)
  async def wrapper(self, interaction: discord.Interaction, steam_id, *args, **kwargs):
    steam_game = await steam.get_game_info(steam_id)
    if not steam_game:
      self.game = None

    if steam_game:
      find_game = await self.bot.database.execute(select(Game).where(Game.steam_id == steam_id))
      game = find_game.scalar_one_or_none()
      if not game:
        game: Game = await self.bot.database.insert(Game(name=steam_game.get('name'), image_url=steam_game.get('image_url'), steam_id=steam_id))

      find_news = await self.bot.database.execute(select(News).where(News.game_id == game.id))
      news = find_news.scalar_one_or_none()
      if not news:
        steam_news = await self.news_service.get_news_by_steam_id(steam_id)
        if steam_news:
          await self.bot.database.insert(News(**steam_news, game_id=game.id))

      self.game = game
    return await func(self, interaction, steam_id, *args, **kwargs)
  
  return wrapper
