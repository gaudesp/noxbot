# src/services/steam.py
import difflib
import json
import re
import aiohttp

class SteamService:
  def __init__(self) -> None:
    """Initialise le service Steam avec les URL d'API nécessaires."""
    self.steam_news_url = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
    self.steam_store_url = "http://store.steampowered.com/api/appdetails"
    self.steam_app_list_url = "http://api.steampowered.com/ISteamApps/GetAppList/v2/"
    self.format = "json"
    self.steam_app_list_data = None

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

  async def get_steam_app_list(self) -> dict | None:
    """Récupère et met en cache la liste complète des applications Steam."""
    if not self.steam_app_list_data:
      self.steam_app_list_data = await self._fetch_json(self.steam_app_list_url)
    return self.steam_app_list_data

  async def search_game_by_name(self, game_name: str) -> list[dict]:
    """Recherche des jeux par nom et retourne les résultats, classés par proximité avec le nom recherché."""
    normalized_game_name = re.sub(r"[-–_:,.]", " ", game_name).lower()
    normalized_game_name = re.sub(r"\s+", " ", normalized_game_name).strip()
    data = await self.get_steam_app_list()
    if not data:
      return []
    app_list = data.get('applist', {}).get('apps', [])
    unique_games = {}
    for app in app_list:
      app_name = app['name']
      normalized_app_name = re.sub(r"[-–_:,.]", " ", app_name).lower() 
      normalized_app_name = re.sub(r"\s+", " ", normalized_app_name).strip()
      if normalized_game_name in normalized_app_name and " - " not in app_name and " – " not in app_name:
        similarity = difflib.SequenceMatcher(None, normalized_game_name, normalized_app_name).ratio()
        if similarity > 0.4:
          unique_games[app_name] = (similarity, app)
    sorted_games = sorted(unique_games.values(), key=lambda x: x[0], reverse=True)
    return [game[1] for game in sorted_games[:25]]

  def get_popular_games(self) -> list[dict]:
    """Récupère la liste des jeux populaires depuis un fichier JSON et les retourne."""
    try:
      with open('src/data/default_games.json', 'r', encoding='utf-8') as file:
        popular_games = json.load(file)
      return popular_games
    except (FileNotFoundError, json.JSONDecodeError):
      return []
