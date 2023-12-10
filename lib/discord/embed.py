import discord
from lib.logging import Logger

logger = Logger('embed')

class Embed:
  def __init__(self):
    self.embed = discord.Embed()

  def for_waven_patchnotes(self, data):
    self.embed.set_author(name="Waven")
    self.embed.set_thumbnail(url="https://www.waven-game.com/build/images/nav/logo.317f2582.png")
    self.embed.color = discord.Color.blue()
    self.embed.title = data['title']
    self.embed.url = data['url']
    self.embed.description = f"Mise à jour effectuée le {data['date']}"
    return self.embed
