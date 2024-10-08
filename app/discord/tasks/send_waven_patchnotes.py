import asyncio
from config import Setting
from lib.file import File
from lib.logging import Logger
from lib.discord.embed import Embed
from models.discord.server import DiscordServer
from models.waven.patchnote import WavenPatchnote
from app.parsers.waven_patchnote_parser import WavenPatchnoteParser

setting = Setting()
patchnote_model = WavenPatchnote()
server_model = DiscordServer()
logger = Logger('waven')

async def send_waven_patchnotes(bot):
  data = File('fixtures/waven/patchnote.html').read()
  patchnotes_found = WavenPatchnoteParser(data).find_patchnotes()

  if patchnotes_found:
    logger.log(f"{len(patchnotes_found)} new patchnotes found on Waven")

    for patchnote in patchnotes_found[::-1]:
      embed = Embed().for_waven_patchnotes(patchnote)
      for server in server_model.find_all():
        channel = bot.get_channel(int(server['waven_channel']))
        if channel:
          await channel.send(embed = embed)
          logger.log(f"Patchnotes {patchnote['title']} sent to {server['name']}")
      await asyncio.sleep(420)
  else:
    logger.log('No new patchnotes found on Waven')
