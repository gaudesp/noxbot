from config import Setting
from lib.file import File
from lib.logging import Logger
from lib.discord.embed import Embed
from models.waven.patchnote import WavenPatchnote
from app.parsers.waven_patchnote_parser import WavenPatchnoteParser

setting = Setting()
patchnote_model = WavenPatchnote()
logger = Logger('waven')

async def send_waven_patchnotes(bot):
  data = File('fixtures/waven/patchnote.html').read()
  patchnote_parser = WavenPatchnoteParser(data)
  patchnotes_found = patchnote_parser.find_patchnotes()

  if patchnotes_found:
    logger_message = f"{len(patchnotes_found)} new patchnotes found on Waven"
    logger.log(logger_message)
    await bot.get_channel(setting.LOGGER_CHANNEL).send(logger_message)

    for patchnote in patchnotes_found[::-1]:
      embed = Embed().for_waven_patchnotes(patchnote)

      await bot.get_channel(setting.WAVEN_CHANNEL).send(embed = embed)
      logger.log(f"Patchnotes {patchnote['title']} sent on channel")
  else:
    logger_message = 'No new patchnotes found on Waven'
    logger.log(logger_message)

    await bot.get_channel(setting.LOGGER_CHANNEL).send(logger_message)
