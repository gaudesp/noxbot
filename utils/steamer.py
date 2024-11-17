import aiohttp
from .matching import Matcher
from typing import Optional

class Steam:
  """Classe utilitaire pour interagir avec l'API Steam et récupérer des informations sur les jeux."""

  def __init__(self) -> None:
    """Initialise les paramètres de l'API Steam."""
    self.format: str = "json"
    self.steam_news_url: str = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
    self.steam_store_url: str = "http://store.steampowered.com/api/appdetails"
    self.steam_app_list_url: str = "http://api.steampowered.com/ISteamApps/GetAppList/v2/"
    self.steam_app_list_data: Optional[dict] = None

  # Public methods

  async def get_game_news(self, app_id: int) -> Optional[dict]:
    """
    Récupère les dernières news pour un jeu spécifique.
    
    :param app_id: ID de l'application du jeu Steam.
    :type app_id: int
    :return: Dernière news du jeu ou None si aucune information n'est disponible.
    :rtype: Optional[dict]
    """
    data: Optional[dict] = await self._fetch_json(self.steam_news_url, params={'appid': app_id, 'format': self.format})
    if data:
      news_items: list[dict] = data.get('appnews', {}).get('newsitems', [])
      for item in news_items:
        if item.get('feedname') == 'steam_community_announcements':
          return item
    return None

  async def get_game_info(self, app_id: int) -> Optional[dict]:
    """
    Récupère les informations de base (nom, image) d'un jeu spécifique.
    
    :param app_id: ID de l'application du jeu Steam.
    :type app_id: int
    :return: Dictionnaire contenant le nom et l'image du jeu ou None si non disponible.
    :rtype: Optional[dict]
    """
    app_data: Optional[dict] = await self._get_app_data(app_id)
    if app_data:
      return {
        'name': app_data.get('name'),
        'header_image': app_data.get('header_image')
      }
    return None

  async def get_steam_app_list(self) -> Optional[dict]:
    """
    Récupère et met en cache la liste complète des applications Steam.
    
    :return: Liste des applications Steam ou None si la récupération échoue.
    :rtype: Optional[dict]
    """
    if not self.steam_app_list_data:
      self.steam_app_list_data = await self._fetch_json(self.steam_app_list_url)
    return self.steam_app_list_data

  async def search_game_by_name(self, game_name: str) -> list[dict]:
    """
    Recherche des jeux par nom et retourne les résultats, classés par proximité avec le nom recherché.
    
    :param game_name: Nom du jeu à rechercher.
    :type game_name: str
    :return: Liste de jeux correspondant au nom, triée par proximité avec le nom recherché.
    :rtype: list[dict]
    """
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

  # Private methods

  async def _fetch_json(self, url: str, params: Optional[dict] = None) -> Optional[dict]:
    """
    Récupère les données JSON depuis une URL donnée.
    
    :param url: URL pour effectuer la requête.
    :type url: str
    :param params: Paramètres additionnels à envoyer avec la requête (facultatif).
    :type params: Optional[dict]
    :return: Données JSON si la requête est réussie, sinon None.
    :rtype: Optional[dict]
    """
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
          if response.status == 200:
            return await response.json()
    except aiohttp.ClientError:
      return None
    return None

  async def _get_app_data(self, app_id: int) -> Optional[dict]:
    """
    Récupère et normalise les données d'un jeu en fonction de son ID d'application.
    
    :param app_id: ID de l'application du jeu Steam.
    :type app_id: int
    :return: Données du jeu ou None si une erreur survient.
    :rtype: Optional[dict]
    """
    data: Optional[dict] = await self._fetch_json(self.steam_store_url, params={'appids': app_id})
    if data and str(app_id) in data and data[str(app_id)]['success']:
      return data[str(app_id)]['data']
    return None
