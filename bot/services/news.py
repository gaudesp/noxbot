from utils.database import Database
from utils.formatting import SteamFormatter
from utils.logging import logger
from utils.steamer import steam

log = logger.get_logger(__name__)

class NewsService():
  def __init__(self, db: Database):
    self.db = db

  async def get_news_by_steam_id(self, steam_id):
    news_for_game = await steam.get_game_news(steam_id)
    
    if not news_for_game or 'gid' not in news_for_game:
      return None
    
    return {
      'title': news_for_game.get('title'),
      'description': SteamFormatter.clean_content(news_for_game.get('contents')),
      'steam_id': news_for_game.get('gid'),
      'url': news_for_game.get('url'),
      'published_date': SteamFormatter.clean_date(news_for_game.get('date')),
      'image_url': SteamFormatter.extract_image(news_for_game.get('contents'))
    }
