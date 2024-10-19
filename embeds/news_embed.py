# services/embeds/news_embeds.py

import discord

class NewsEmbed:
  def __init__(self, title, url, description, color=discord.Color.blue(), game_name=None, image_url=None):
    self.title = title
    self.url = url
    self.description = description
    self.color = color
    self.game_name = game_name
    self.image_url = image_url

  def create(self):
    embed = discord.Embed(
      title=self.title,
      url=self.url,
      description=self.description,
      color=self.color
    )
    if self.game_name:
      embed.set_author(name=self.game_name)
    if self.image_url:
      embed.set_image(url=self.image_url)
    return embed
