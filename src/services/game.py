# src/services/game.py
from src.services.news import NewsService
from src.repositories.game import GameRepository
from src.models.game import Game as GameModel
from src.schemas.game import Game
from src.utils.discord import DiscordBot

class GameService:
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le service de jeu avec le bot Discord."""
    self.bot = bot
    self.game_repository = GameRepository(bot)
    self.news_service = NewsService(bot, self)

  async def add_game(self, app_id: int, guild_id: int, channel_id: int, game_name: str) -> Game:
    """Ajoute un nouveau jeu et met à jour les dernières nouvelles."""
    game = await self.game_repository.create_one(app_id, guild_id, channel_id, game_name)
    await self.news_service.update_last_news(game.id, game.guild_id)
    return game

  async def find_all_games(self) -> list[GameModel]:
    """Récupère tous les jeux disponibles."""
    games = await self.game_repository.get_all()
    return games
  
  async def find_game_for_guild(self, app_id: int, guild_id: int) -> GameModel | None:
    """Récupère un jeu par son identifiant et l'identifiant de la guilde."""
    game = await self.game_repository.get_one_by_guild(app_id, guild_id)
    return game
  
  async def find_games_for_guild(self, guild_id: int) -> list[GameModel]:
    """Récupère tous les jeux associés à une guilde spécifique."""
    games = await self.game_repository.get_all_by_guild(guild_id)
    return sorted(games, key=lambda game: game.name.lower())

  async def update_game_last_news_id(self, app_id: int, guild_id: int, last_news_id: str) -> bool:
    """Met à jour l'identifiant de la dernière nouvelle d'un jeu."""
    game = await self.find_game_for_guild(app_id, guild_id)
    if game:
      await self.game_repository.update_one(game, {"last_news_id": last_news_id})
      return True
    return False

  async def delete_game(self, app_id: int, guild_id: int) -> GameModel | bool:
    """Supprime un jeu de la guilde."""
    game = await self.find_game_for_guild(app_id, guild_id)
    if game:
      await self.game_repository.delete_one_or_many(game)
      return game
    return False

  async def delete_games(self, guild_id: int) -> list[str]:
    """Supprime tous les jeux associés à une guilde."""
    games = await self.find_games_for_guild(guild_id)
    deleted_game_names = [f"`{game.name}`" for game in games] 
    if deleted_game_names:
      await self.game_repository.delete_one_or_many(games)
    return ', '.join(deleted_game_names)
