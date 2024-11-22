from functools import wraps
import discord
from sqlalchemy.future import select
from models import Game
from utils.steamer import steam

def ensure_game(func):
  @wraps(func)
  async def wrapper(self, interaction: discord.Interaction, steam_id, *args, **kwargs):
    steam_game = await steam.get_game_info(steam_id)
    if not steam_game:
      await interaction.followup.send(f"Le jeu est introuvable sur Steam.")
      return
  
    find_game = await self.bot.database.execute(select(Game).where(Game.steam_id == steam_id))
    game = find_game.scalar_one_or_none()
    if not game:
      game: Game = await self.bot.database.insert(Game(name=steam_game.get('name'), image_url=steam_game.get('image_url'), steam_id=steam_id))

    self.game = game
    return await func(self, interaction, steam_id, *args, **kwargs)
  
  return wrapper
