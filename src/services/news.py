# src/services/news.py

from collections import defaultdict
from datetime import datetime
from logging import WARNING
from typing import Dict, List, Optional, Tuple
from src.services.guild import GuildService
from src.utils.embed import NewsEmbed
from src.services.steam import SteamService
from src.schemas.game import Game
from src.utils.formatter import NewsFormatter

class NewsService:
  def __init__(self, bot: any, game_service: any) -> None:
    """Initialise le service de news avec le bot et le service de jeu."""
    self.bot = bot
    self.game_service = game_service
    self.guild_service = GuildService(bot)
    self.steam_service = SteamService()

  # Public methods

  async def send_all_news(self) -> None:
    """Récupère toutes les news pour les jeux suivis."""
    games_by_app_id = await self._group_games_by_app_id()
    for app_id, game_instances in games_by_app_id.items():
      try:
        await self._check_news_for_games(app_id, game_instances)
      except:
        continue

  async def send_last_news(self, game: Game, check_last_news: Optional[bool] = False) -> Optional[bool]:
    """Récupère les dernières news pour un jeu spécifique."""
    game_instance = Game.model_validate(game)
    return await self._check_news_for_games(game.id, [game_instance], check_last_news)

  async def update_last_news(self, app_id: int, guild_id: int) -> None:
    """Met à jour l'ID de la dernière news pour un jeu."""
    news = await self.steam_service.get_game_news(app_id)
    if news and 'gid' in news:
      await self.game_service.update_game_last_news_id(app_id, guild_id, news.get('gid'))

  # Private methods

  async def _check_news_for_games(self, app_id: int, game_instances: List[Game], check_last_news: bool = True) -> bool:
    """Vérifie les news pour un groupe de jeux."""
    try:
      news = await self.steam_service.get_game_news(app_id)
      if news and 'gid' in news:
        return await self._process_news_for_games(news, game_instances, check_last_news)
    except Exception as e:
      self.bot.log(f"Failed to retrieve news for app_id {app_id}: {e}", "discord.check_news_for_game", WARNING)
    return False

  async def _process_news_for_games(self, news: Dict, game_instances: List[Game], check_last_news: Optional[bool]) -> bool:
    """Traite les news pour les instances de jeux et les envoie si nécessaire."""
    has_news = False
    for game in game_instances:
      if not check_last_news or news.get('gid') != game.last_news_id:
        await self._send_news_to_channel(news, game)
        has_news = True
    return has_news

  async def _send_news_to_channel(self, news: Dict, game: Game) -> None:
    """Envoie les dernières news à un canal spécifique."""
    guild_id = game.guild_id
    title = news.get('title')
    description = NewsFormatter.clean_content(news.get('contents'))
    channel = self._get_channel(game.channel_id)
    await self._send_last_news(news, game.id, guild_id, channel, game.name, title, description)

  async def _send_last_news(self, news: Dict, app_id: int, guild_id: int, channel: any, game_name: str, title: str, description: str) -> None:
    """Envoie les dernières news à un canal spécifique."""
    image_url = await self._get_image_url(news, app_id)
    published_date = self._extract_published_date(news)
    embed = await self._create_news_embed(guild_id, game_name, image_url, published_date, title, description, news.get('url'))
    await channel.send(embed=embed)
    await self.game_service.update_game_last_news_id(app_id, guild_id, news.get('gid'))

  async def _get_image_url(self, news: Dict, app_id: int) -> str:
    """Récupère l'URL de l'image à partir du contenu des news."""
    contents = news.get('contents')
    image_urls = NewsFormatter.extract_image_urls(contents)
    return image_urls[0] if image_urls else await self.steam_service.get_game_image_url(app_id)

  async def _create_news_embed(self, guild_id: int, game_name: str, image_url: str, published_date: Optional[datetime], title: str, description: str, url: str) -> NewsEmbed:
    """Crée un embed de news avec les informations fournies."""
    locale = await self.guild_service.find_guild_locale(guild_id)
    return NewsEmbed(
      i18n=self.bot.i18n,
      locale=locale,
      title=title,
      url=url,
      description=description,
      published_date=published_date,
      game_name=game_name,
      image_url=image_url
    ).create()

  async def _group_games_by_app_id(self) -> Dict[int, List[Game]]:
    """Groupe les jeux par leur ID d'application."""
    games_by_app_id = defaultdict(list)
    games = await self.game_service.find_all_games()
    for game in games:
      games_by_app_id[game.id].append(Game.model_validate(game))
    return games_by_app_id

  def _get_channel(self, channel_id: int) -> any:
    """Récupère le canal Discord correspondant à l'ID fourni."""
    return self.bot.get_channel(int(channel_id))

  def _extract_published_date(self, news: Dict) -> Optional[datetime]:
    """Extrait la date de publication à partir des news."""
    timestamp = news.get('date')
    return datetime.fromtimestamp(timestamp) if timestamp else None
