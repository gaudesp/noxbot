# src/repositories/game.py
from sqlalchemy import update, delete
from sqlalchemy.future import select
from src.models.game import Game as GameModel
from src.utils.discord import DiscordBot

class GameRepository:
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le dépôt de jeux avec le bot Discord."""
    self.bot = bot

  async def add_game(self, app_id: int, guild_id: int, channel_id: int, game_name: str) -> GameModel:
    """Ajoute un jeu à la base de données et retourne l'entité insérée."""
    game = GameModel(app_id=app_id, guild_id=guild_id, channel_id=channel_id, game_name=game_name)
    return await self.bot.database.insert(game)

  async def get_all_games(self) -> list[GameModel]:
    """Retourne tous les jeux de la base de données."""
    games = await self.bot.database.execute(select(GameModel))
    return games.scalars().all()
  
  async def get_game_for_guild(self, app_id: int, guild_id: int) -> GameModel | None:
    """Retourne le jeu pour un serveur spécifique ou None s'il n'existe pas."""
    game = await self.bot.database.execute(select(GameModel).where(GameModel.app_id == app_id, GameModel.guild_id == guild_id))
    return game.scalar_one_or_none()
  
  async def get_games_for_guild(self, guild_id: int) -> list[GameModel]:
    """Retourne tous les jeux associés à un serveur spécifique."""
    games = await self.bot.database.execute(select(GameModel).where(GameModel.guild_id == guild_id))
    return games.scalars().all()

  async def update_last_news_id(self, app_id: int, guild_id: int, news_id: str) -> bool:
    """Met à jour l'ID de la dernière nouvelle pour un jeu spécifique et retourne un boolean."""
    game = await self.get_game_for_guild(app_id, guild_id)
    if game:
      await self.bot.database.execute(update(GameModel).where(GameModel.app_id == app_id, GameModel.guild_id == guild_id).values(last_news_id=news_id))
      return True
    return False

  async def delete_game(self, app_id: int, guild_id: int) -> GameModel | bool:
    """Supprime un jeu spécifique de la base de données et retourne l'entité supprimée, ou False si le jeu n'existe pas."""
    game = await self.get_game_for_guild(app_id, guild_id)
    if game:
      await self.bot.database.execute(delete(GameModel).where(GameModel.app_id == app_id, GameModel.guild_id == guild_id))
      return game
    return False

  async def delete_all_games(self, guild_id: int) -> int:
    """Supprime tous les jeux associés à un serveur et retourne le nombre de jeux supprimés."""
    games = await self.get_games_for_guild(guild_id)
    count_deleted = len(games)
    if count_deleted > 0:
      await self.bot.database.execute(delete(GameModel).where(GameModel.guild_id == guild_id))
    return count_deleted
