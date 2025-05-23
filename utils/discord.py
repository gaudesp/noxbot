import os
import discord
from datetime import datetime
from discord.ext import commands
from config import config
from utils.database import Database, database
from utils.logging import logger

log = logger.get_logger(__name__)

class DiscordBot(commands.Bot):
  database: Database = database
  uptime: datetime = datetime.now()

  def __init__(self, **kwargs) -> None:
    kwargs.setdefault("activity", discord.Activity(type=discord.ActivityType.listening, name="NOKX"))
    kwargs.setdefault("allowed_mentions", discord.AllowedMentions(everyone=False))
    kwargs.setdefault("case_insensitive", True)
    kwargs.setdefault("intents", discord.Intents.all())
    kwargs.setdefault("max_messages", 2500)
    kwargs.setdefault("status", discord.Status.online)
    super().__init__(command_prefix='/', **kwargs)
    self.owner_id = config.discord_owner_id

  async def on_ready(self) -> None:
    log.info(f"{self.user} is online | Server(s) : {len(self.guilds)}")

  async def setup_hook(self) -> None:
    await self._init_database()
    await self._load_extensions()
    await self._sync_commands()
    log.info("Initial BOT setup completed.")

  async def close(self) -> None:
    log.info("Closing BOT...")
    await self.database.close()
    await super().close()

  async def _init_database(self) -> None:
    await self.database.setup()
    log.info("Database connection established")

  async def _load_extensions(self) -> None:
    for cog_folder in os.listdir('./bot/cogs'):
      cog_path = os.path.join('./bot/cogs', cog_folder)
      if os.path.isdir(cog_path):
        cog_files_loaded = []
        for root, _, files in os.walk(cog_path):
          for filename in files:
            if filename.endswith('.py') and filename != '__init__.py':
              extension = f"bot.cogs.{os.path.relpath(root, './bot/cogs').replace(os.sep, '.')}.{filename[:-3]}"
              try:
                await self.load_extension(extension)
                cog_files_loaded.append(extension)
              except Exception as e:
                log.error(f"Failed to load {extension}: {e}")
        if cog_files_loaded:
          log.info(f"{cog_folder.capitalize()} cog loaded with {len(cog_files_loaded)} file(s)")

  async def _sync_commands(self) -> None:
    synced = await self.tree.sync()
    log.info(f"{len(synced)} command(s) synced : {', '.join(command.name for command in synced)}")

class NewsEmbed:
  def __init__(self, news: dict, game: dict, color=discord.Color.blue()) -> None:
    self.news = news
    self.game = game
    self.color = color

  def create(self) -> discord.Embed:
    embed = discord.Embed(
      title=self.news.get('title'),
      url=self.news.get('url'),
      description=self.news.get('description'),
      color=self.color
    )
    self._add_author(embed)
    self._add_image(embed)
    self._add_footer(embed)
    return embed

  def _add_author(self, embed: discord.Embed) -> None:
    if self.game.get('name'):
      embed.set_author(name=self.game.get('name'))

  def _add_image(self, embed: discord.Embed) -> None:
    if self.news.get('image_url'):
      image_url = self.news.get('image_url')
    elif self.game.get('image_url'):
      image_url = self.game.get('image_url')
    else:
      return
    embed.set_image(url=image_url)

  def _add_footer(self, embed: discord.Embed) -> None:
    if self.news.get('published_date'):
      formatted_date = self.news.get('published_date').strftime("%m/%d/%Y at %I:%M %p")
      embed.set_footer(text=f"Posted on {formatted_date}")

bot = DiscordBot()
logger.get_logger("discord")
