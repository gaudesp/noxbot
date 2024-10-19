# services/embeds/news_embeds.py

import discord

from helpers.news_helper import clean_news_content

class NewsEmbed:
  def __init__(self, title, url, description, game_name=None, image_url=None, color=discord.Color.blue()):
    self.title = title
    self.url = url
    self.description = self._clean_description(description)
    self.game_name = game_name
    self.image_url = image_url
    self.color = color

  def _clean_description(self, description):
    cleaned = clean_news_content(description)
    return cleaned[:300] + "..." if len(cleaned) > 300 else cleaned

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
