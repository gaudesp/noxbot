# src/services/steam.py
import aiohttp

class SteamService:
  def __init__(self) -> None:
    """Initialise le service Steam avec les URL d'API nécessaires."""
    self.steam_news_url = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
    self.steam_store_url = "http://store.steampowered.com/api/appdetails"
    self.steam_app_list_url = "http://api.steampowered.com/ISteamApps/GetAppList/v2/"
    self.format = "json"

  async def _fetch_json(self, url: str, params: dict = None) -> dict | None:
    """Récupère les données JSON d'une URL donnée."""
    async with aiohttp.ClientSession() as session:
      async with session.get(url, params=params) as response:
        if response.status == 200:
          return await response.json()
    return None

  async def get_game_news(self, app_id: int) -> dict | None:
    """Récupère les dernières news pour un jeu spécifique."""
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

  async def get_game_image_url(self, app_id: int) -> str | None:
    """Récupère l'URL de l'image d'un jeu spécifique."""
    url = f"{self.steam_store_url}?appids={app_id}"
    data = await self._fetch_json(url)
    if data and str(app_id) in data and data[str(app_id)]['success']:
      return data[str(app_id)]['data'].get('header_image')
    return None

  async def get_game_name(self, app_id: int) -> str | None:
    """Récupère le nom d'un jeu à partir de son ID d'application."""
    url = f"{self.steam_store_url}?appids={app_id}"
    data = await self._fetch_json(url)
    if data and str(app_id) in data and data[str(app_id)]['success']:
      return data[str(app_id)]['data'].get('name')
    return None

  async def search_game_by_name(self, game_name: str) -> list[dict] | list:
    """Recherche des jeux par nom et retourne les résultats, en excluant les DLC."""
    url = self.steam_app_list_url
    data = await self._fetch_json(url)
    if data:
      app_list = data.get('applist', {}).get('apps', [])
      unique_games = {}
      for app in app_list:
        if (game_name.lower() in app['name'].lower() 
          and " - " not in app['name'] 
          and " – " not in app['name']):
          unique_games[app['name']] = app
      return list(unique_games.values())[:25]
    return []
