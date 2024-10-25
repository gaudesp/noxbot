# src/services/news.py
from collections import defaultdict
from datetime import datetime
from src.utils.helper import extract_image_urls
from src.utils.embed import NewsEmbed
from src.services.steam import SteamService
from src.schemas.game import Game

class NewsService:
  def __init__(self, bot, game_service) -> None:
    """Initialise le service de news avec le bot et le service de jeu."""
    self.bot = bot
    self.game_service = game_service
    self.steam_service = SteamService()

  async def get_all_news(self) -> None:
    """Récupère toutes les news pour les jeux suivis."""
    games_by_app_id = await self._group_games_by_app_id()
    for app_id, game_instances in games_by_app_id.items():
      await self._check_news_for_games(app_id, game_instances)

  async def get_last_news(self, game: Game, check_last_news: bool = False) -> bool:
    """Récupère les dernières news pour un jeu spécifique."""
    game_instance = Game.model_validate(game)
    return await self._check_news_for_games(game.id, [game_instance], check_last_news)

  async def update_last_news(self, app_id: int, guild_id: int) -> None:
    """Met à jour l'ID de la dernière news pour un jeu."""
    news = await self.steam_service.get_game_news(app_id)
    if news and 'gid' in news:
      await self.game_service.update_game_last_news_id(app_id, guild_id, news.get('gid'))

  async def _check_news_for_games(self, app_id: int, game_instances: list[Game], check_last_news: bool = True) -> bool:
    """Vérifie les news pour un groupe de jeux."""
    news = await self.steam_service.get_game_news(app_id)
    has_news = False
    if news and 'gid' in news:
      for game in game_instances:
        if not check_last_news or news.get('gid') != game.last_news_id:
          channel = self._get_channel(game.channel_id)
          if channel:
            await self._send_last_news(news, game.id, game.guild_id, channel, game.name)
            has_news = True
    return has_news

  async def _send_last_news(self, news, app_id: int, guild_id: int, channel, game_name: str) -> None:
    """Envoie les dernières news à un canal spécifique."""
    image_url = await self._get_image_url(news, app_id)
    published_date = self._extract_published_date(news)
    embed = self._create_news_embed(news, game_name, image_url, published_date)
    await channel.send(embed=embed)
    await self.game_service.update_game_last_news_id(app_id, guild_id, news.get('gid'))

  async def _get_image_url(self, news, app_id: int) -> str:
    """Récupère l'URL de l'image à partir du contenu des news."""
    contents = news.get('contents')
    image_urls = extract_image_urls(contents)
    return image_urls[0] if image_urls else await self.steam_service.get_game_image_url(app_id)

  def _create_news_embed(self, news, game_name: str, image_url: str, published_date) -> NewsEmbed:
    """Crée un embed de news avec les informations fournies."""
    return NewsEmbed(
      title=news.get('title'),
      url=news.get('url'),
      description=news.get('contents'),
      published_date=published_date,
      game_name=game_name,
      image_url=image_url
    ).create()

  async def _group_games_by_app_id(self) -> dict[int, list[Game]]:
    """Groupe les jeux par leur ID d'application."""
    games_by_app_id = defaultdict(list)
    games = await self.game_service.find_all_games()
    for game in games:
      games_by_app_id[game.id].append(Game.model_validate(game))
    return games_by_app_id

  def _get_channel(self, channel_id: int):
    """Récupère le canal Discord correspondant à l'ID fourni."""
    return self.bot.get_channel(int(channel_id))

  def _extract_published_date(self, news) -> datetime:
    """Extrait la date de publication à partir des news."""
    timestamp = news.get('date')
    return datetime.fromtimestamp(timestamp) if timestamp else None
