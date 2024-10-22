# utils/discord_bot.py
from datetime import datetime
import discord
from discord.ext import commands
from logging import Logger, INFO
from typing import TypeVar
from config.settings import Settings
from config.database import Database
from discord import __version__ as discord_version

Self = TypeVar("Self", bound="DiscordBot")

class DiscordBot(commands.Bot):
  settings: Settings
  logger: Logger
  database: Database
  uptime: datetime = datetime.now()

  def __init__(self, **kwargs):
    kwargs.setdefault("activity", discord.Activity(type=discord.ActivityType.listening, name="NOKX"))
    kwargs.setdefault("allowed_mentions", discord.AllowedMentions(everyone=False))
    kwargs.setdefault("case_insensitive", True)
    kwargs.setdefault("intents", discord.Intents.all())
    kwargs.setdefault("max_messages", 2500)
    kwargs.setdefault("status", discord.Status.online)

    super().__init__(command_prefix='/', **kwargs)

  def log(self, message: str, name: str, level: int = INFO, **kwargs):
    self.logger.name = name
    self.logger.log(level = level, msg = message, **kwargs)

  async def on_ready(self):
    self.log(f"Logged as {self.user} | Discord.py v{discord_version} | Guilds : {len(self.guilds)}", "discord.on_ready")

  async def startup(self):
    self.appinfo = await self.application_info()
    await self.wait_until_ready()
    await self.__sync_commands()

  async def setup_hook(self):
    await self.__init_database()
    await self.__load_extensions()
    await self.__create_tasks()

  async def close(self):
    await self.database.close()
    await super().close()

  async def __init_database(self):
    self.database = Database()
    await self.database.setup()
    self.log("Database connection established", "discord.init_database")

  async def __load_extensions(self):
    extensions = ['src.cogs.error_cog', 'src.cogs.game_cog']
    for extension in extensions:
      await self.load_extension(extension)
    self.log(f"{len(extensions)} cogs loaded : {', '.join(extension.split('.')[-1] for extension in extensions)}", "discord.load_extensions")

  async def __create_tasks(self):
    tasks = [self.startup()]
    for task in tasks:
      self.loop.create_task(task)

  async def __sync_commands(self):
    synced = await self.tree.sync()
    self.log(f"Application commands synced ({len(synced)})", "discord.startup")
