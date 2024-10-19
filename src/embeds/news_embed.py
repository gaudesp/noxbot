# src/embeds/news_embeds.py
import discord
from datetime import datetime
from src.helpers.news_helper import clean_news_content

class NewsEmbed:
  def __init__(self, title, url, description, published_date=None, game_name=None, image_url=None, small_image_url=None, color=discord.Color.blue()):
    self.title = title
    self.url = url
    self.description = self._clean_description(description)
    self.published_date = self._format_date(published_date)
    self.game_name = game_name
    self.image_url = image_url
    self.small_image_url = small_image_url
    self.color = color

  def _clean_description(self, description):
    cleaned = clean_news_content(description)
    return cleaned[:300] + "..." if len(cleaned) > 300 else cleaned

  def _format_date(self, published_date):
    if published_date:
      return published_date.strftime("%d/%m/%Y à %Hh%M")
    return "Date non spécifiée"

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
    if self.small_image_url:
      embed.set_thumbnail(url=self.small_image_url)
    if self.published_date:
      embed.set_footer(text=f"Publié le {self.published_date}")
    return embed
