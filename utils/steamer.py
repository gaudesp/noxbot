import aiohttp
from typing import Optional
from utils.matching import Matcher

class Steam:
  def __init__(self) -> None:
    self.format: str = "json"
    self.steam_news_url: str = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
    self.steam_store_url: str = "http://store.steampowered.com/api/appdetails"
    self.steam_app_list_url: str = "http://api.steampowered.com/ISteamApps/GetAppList/v2/"
    self.steam_app_list_data: Optional[dict] = None

  async def get_game_news(self, app_id: int) -> Optional[dict]:
    data: Optional[dict] = await self._fetch_json(self.steam_news_url, params={'appid': app_id, 'format': self.format})
    if data:
      news_items: list[dict] = data.get('appnews', {}).get('newsitems', [])
      for item in news_items:
        if item.get('feedname') == 'steam_community_announcements':
          return item
    return None

  async def get_game_info(self, app_id: int) -> Optional[dict]:
    app_data: Optional[dict] = await self._get_app_data(app_id)
    if app_data:
      return {
        'name': app_data.get('name'),
        'image_url': app_data.get('header_image')
      }
    return None

  async def get_steam_app_list(self) -> Optional[dict]:
    if not self.steam_app_list_data:
      self.steam_app_list_data = await self._fetch_json(self.steam_app_list_url)
    return self.steam_app_list_data

  async def search_game_by_name(self, game_name: str) -> list[dict]:
    data: Optional[dict] = await self.get_steam_app_list()
    if not data:
      return []
    app_list: list[dict] = data.get('applist', {}).get('apps', [])
    return Matcher.search_and_sort_by_string(
      search_string=game_name,
      items=app_list,
      key='name',
      threshold=0.4
    )

  async def _fetch_json(self, url: str, params: Optional[dict] = None) -> Optional[dict]:
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
          if response.status == 200:
            return await response.json()
    except aiohttp.ClientError:
      return None
    return None

  async def _get_app_data(self, app_id: int) -> Optional[dict]:
    data: Optional[dict] = await self._fetch_json(self.steam_store_url, params={'appids': app_id})
    if data and str(app_id) in data and data[str(app_id)]['success']:
      return data[str(app_id)]['data']
    return None

steam = Steam()
