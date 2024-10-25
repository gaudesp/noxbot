# src/repositories/game.py
from sqlalchemy import update, delete
from sqlalchemy.future import select
from src.schemas.game import Game
from src.models.game import Game as GameModel
from src.utils.discord import DiscordBot

class GameRepository:
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le dépôt de jeux avec le bot Discord."""
    self.bot = bot

  async def create_one(self, app_id: int, guild_id: int, channel_id: int, game_name: str) -> Game:
    """Crée un nouveau jeu et l'insère dans la base de données."""
    game = GameModel(id=app_id, guild_id=guild_id, channel_id=channel_id, name=game_name)
    return await self.bot.database.insert(game)

  async def get_all(self) -> list[GameModel]:
    """Récupère tous les jeux de la base de données."""
    games = await self.bot.database.execute(select(GameModel))
    return games.scalars().all()
  
  async def get_one_by_guild(self, app_id: int, guild_id: int) -> Game | None:
    """Récupère un jeu par son identifiant et l'identifiant de la guilde."""
    game = await self.bot.database.execute(select(GameModel).where(GameModel.id == app_id, GameModel.guild_id == guild_id))
    return game.scalar_one_or_none()
  
  async def get_all_by_guild(self, guild_id: int) -> list[Game]:
    """Récupère tous les jeux associés à une guilde."""
    games = await self.bot.database.execute(select(GameModel).where(GameModel.guild_id == guild_id))
    return games.scalars().all()

  async def update_one(self, game: Game, values: dict) -> bool:
    """Met à jour un jeu avec les valeurs fournies."""
    await self.bot.database.execute(update(GameModel).where(GameModel.id == game.id, GameModel.guild_id == game.guild_id).values(**values))
    return True

  async def delete_one_or_many(self, game: Game | list[Game]) -> Game | bool:
    """Supprime un ou plusieurs jeux de la base de données."""
    await self.bot.database.delete(game)
    return True
