# src/services/news_service.py
from collections import defaultdict
from datetime import datetime
from src.helpers.news_helper import extract_image_urls
from src.embeds.news_embed import NewsEmbed
from src.services.steam_service import SteamService
from src.repositories import game_repository
from src.schemas.game_schema import GameSchema

class NewsService:
    def __init__(self, bot):
      self.bot = bot
      self.steam_service = SteamService()

    async def get_all_news(self):
      games_by_app_id = self._group_games_by_app_id()
      for app_id, game_instances in games_by_app_id.items():
        await self._check_news_for_games(app_id, game_instances)

    async def get_last_news(self, game, check_last_news=False):
      game_instance = GameSchema.model_validate(game)
      return await self._check_news_for_games(game.app_id, [game_instance], check_last_news)

    async def update_last_news(self, app_id, guild_id):
      news = await self.steam_service.get_game_news(app_id)
      if news and 'gid' in news:
        game_repository.update_last_news_id(app_id, guild_id, news.get('gid'))

    async def _check_news_for_games(self, app_id, game_instances, check_last_news=True):
      news = await self.steam_service.get_game_news(app_id)
      has_news = False
      if news and 'gid' in news:
        for game in game_instances:
          if not check_last_news or news.get('gid') != game.last_news_id:
            channel = self._get_channel(game.channel_id)
            if channel:
              await self._send_last_news(news, game.app_id, game.guild_id, channel, game.game_name)
              has_news = True
      return has_news

    async def _send_last_news(self, news, app_id, guild_id, channel, game_name):
      image_url = await self._get_image_url(news, app_id)
      small_image_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{app_id}/capsule_184x69.jpg"
      published_date = self._extract_published_date(news)
      embed = self._create_news_embed(news, game_name, image_url, published_date, small_image_url)
      await channel.send(embed=embed)
      game_repository.update_last_news_id(app_id, guild_id, news.get('gid'))

    async def _get_image_url(self, news, app_id):
      contents = news.get('contents')
      image_urls = extract_image_urls(contents)
      return image_urls[0] if image_urls else await self.steam_service.get_game_image_url(app_id)

    def _create_news_embed(self, news, game_name, image_url, published_date, small_image_url):
      return NewsEmbed(
        title=news.get('title'),
        url=news.get('url'),
        description=news.get('contents'),
        published_date=published_date,
        game_name=game_name,
        image_url=image_url,
        small_image_url=small_image_url
      ).create()

    def _group_games_by_app_id(self):
      games_by_app_id = defaultdict(list)
      games = game_repository.get_all_games()
      for game in games:
        games_by_app_id[game.app_id].append(GameSchema.model_validate(game))
      return games_by_app_id

    def _get_channel(self, channel_id):
      return self.bot.get_channel(int(channel_id))

    def _extract_published_date(self, news):
      timestamp = news.get('date')
      return datetime.fromtimestamp(timestamp) if timestamp else None