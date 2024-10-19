# services/steam_services.py
import aiohttp
from config import STEAM_API_KEY
from src.utils.logger import logger

class SteamService:
  def __init__(self):
    self.steam_news_url = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
    self.steam_store_url = "http://store.steampowered.com/api/appdetails"
    self.steam_app_list_url = "http://api.steampowered.com/ISteamApps/GetAppList/v2/"
    self.format = "json"

  async def _fetch_json(self, url, params=None):
    async with aiohttp.ClientSession() as session:
      try:
        async with session.get(url, params=params) as response:
          if response.status == 200:
            return await response.json()
          else:
            logger.log(f"Erreur HTTP {response.status} pour l'URL {url}", 'error')
      except aiohttp.ClientError as e:
        logger.log(f"Erreur lors de la connexion à {url}: {e}", 'error')
    return None

  async def get_game_news(self, app_id):
    url = self.steam_news_url
    params = {
      'appid': app_id,
      'format': self.format
    }
    data = await self._fetch_json(url, params)
    if data:
      news_items = data.get('appnews', {}).get('newsitems', [])
      if news_items:
        for item in news_items:
          if item.get('feedname') == 'steam_community_announcements':
            return item
    return None

  async def get_game_image_url(self, app_id):
    url = f"{self.steam_store_url}?appids={app_id}"
    data = await self._fetch_json(url)
    if data and str(app_id) in data and data[str(app_id)]['success']:
      return data[str(app_id)]['data'].get('header_image')
    return None

  async def get_game_name(self, app_id):
    url = f"{self.steam_store_url}?appids={app_id}"
    data = await self._fetch_json(url)
    if data and str(app_id) in data and data[str(app_id)]['success']:
      return data[str(app_id)]['data'].get('name')
    return None

  async def search_game_by_name(self, game_name):
    url = self.steam_app_list_url
    data = await self._fetch_json(url)
    if data:
      app_list = data.get('applist', {}).get('apps', [])
      matching_games = [app for app in app_list if game_name.lower() in app['name'].lower()]
      return matching_games[:25]
    return None
