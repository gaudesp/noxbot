import uuid
from config import Setting
from lib.logging import Logger
from scrappeycom.scrappey import Scrappey

setting = Setting()
logger = Logger('scrappey')

class Scrapper:
  def __init__(self):
    self.sessionData = {
      'session': str(uuid.uuid4())
    }
    self.scrappey = self.init_scrapper()
    self.session = self.create_session()

  def init_scrapper(self):
    logger.log('Initializing Scrappey')
    scrapper = Scrappey(setting.SCRAPPEY_TOKEN)
    return scrapper
    
  def create_session(self):
    session = self.scrappey.create_session(self.sessionData)
    logger.log(f"Session {session['session']} created")
    return session
    
  def destroy_session(self):
    self.scrappey.destroy_session(self.sessionData)
    logger.log(f"Session {self.sessionData['session']} destroyed")
    
  #je trouve pas ça très intuitif que le get_data fasse aussi la destruction de la session alors qu'il ne fait pas également la creation
  async def get_data(self, url):
    logger.log(f"Scrapping data from {url}")
    data = self.scrappey.get({ 'session': self.session, 'url': url })
    self.destroy_session()
    return data['solution']['response']
