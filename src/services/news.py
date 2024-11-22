from utils.database import Database
from utils.formatting import SteamFormatter
from utils.logging import logger
from utils.steamer import steam

log = logger.get_logger(__name__)

class NewsService():
  def __init__(self, db: Database):
    self.db = db

  async def get_news_by_steam_id(self, steam_id):
    log.info(f"Traitement des actualités pour le jeu {steam_id}...")
    
    news_for_game = await steam.get_game_news(steam_id)
    game_info = await steam.get_game_info(steam_id)
    
    if not news_for_game or 'gid' not in news_for_game:
      log.warning(f"Aucune actualité trouvée pour le jeu {game_info.get('name')}.")
      return None
    
    log.info(f"Actualité {news_for_game.get('gid')} trouvée pour le jeu {game_info.get('name')}.")
    
    return {
      'title': news_for_game.get('title'),
      'description': SteamFormatter.clean_content(news_for_game.get('contents')),
      'steam_id': news_for_game.get('gid'),
      'url': news_for_game.get('url'),
      'published_date': SteamFormatter.clean_date(news_for_game.get('date')),
      'image_url': SteamFormatter.extract_image(news_for_game.get('contents'))
    }
