from config import Setting
from lib.file import File
from lib.scrappey import Scrapper

setting = Setting()

async def scrape_waven_patchnotes():
  if setting.BOT_ENV != 'PROD':
    return
  
  scrapper = Scrapper()
  data = await scrapper.get_data('https://forum.waven-game.com/en/44-patchnotes-fr')

  if data:
    File('fixtures/waven/patchnote.html').store(data)
