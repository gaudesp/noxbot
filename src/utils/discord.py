# src/utils/discord.py
import os
import discord
from datetime import datetime
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

  def __init__(self, **kwargs) -> None:
    """Initialise le bot Discord avec les paramètres par défaut."""
    kwargs.setdefault("activity", discord.Activity(type=discord.ActivityType.listening, name="NOKX"))
    kwargs.setdefault("allowed_mentions", discord.AllowedMentions(everyone=False))
    kwargs.setdefault("case_insensitive", True)
    kwargs.setdefault("intents", discord.Intents.all())
    kwargs.setdefault("max_messages", 2500)
    kwargs.setdefault("status", discord.Status.online)

    super().__init__(command_prefix='/', **kwargs)

  def log(self, message: str, name: str, level: int = INFO, **kwargs) -> None:
    """Enregistre un message dans le journal avec le niveau de gravité spécifié."""
    self.logger.name = name
    self.logger.log(level=level, msg=message, **kwargs)

  async def on_ready(self) -> None:
    """Appelé lorsque le bot est prêt et connecté à Discord."""
    self.log(f"Logged as {self.user} | Discord.py v{discord_version} | Guilds : {len(self.guilds)}", "discord.on_ready")

  async def startup(self) -> None:
    """Prépare le bot après sa connexion à Discord."""
    self.appinfo = await self.application_info()
    await self.wait_until_ready()
    await self.__sync_commands()

  async def setup_hook(self) -> None:
    """Configurer le bot, y compris la base de données et les extensions."""
    await self.__init_database()
    await self.__load_extensions()
    self.loop.create_task(self.startup())

  async def close(self) -> None:
    """Ferme la connexion à la base de données et déconnecte le bot."""
    await self.database.close()
    await super().close()

  async def __init_database(self) -> None:
    """Initialise la connexion à la base de données."""
    self.database = Database(self.settings.db_path)
    await self.database.setup()
    self.log("Database connection established", "discord.init_database")

  async def __load_extensions(self) -> None:
    """Charge toutes les extensions (cogs) du bot."""
    extensions = [
      f'src.cogs.{filename[:-3]}'
      for filename in os.listdir('src/cogs')
      if filename.endswith('.py') and filename != '__init__.py'
    ]
    for extension in extensions:
      await self.load_extension(extension)
    self.log(f"{len(extensions)} cogs loaded : {', '.join(extension.split('.')[-1] for extension in extensions)}", "discord.load_extensions")

  async def __sync_commands(self) -> None:
    """Synchronise les commandes de l'application avec Discord."""
    synced = await self.tree.sync()
    self.log(f"Application commands synced ({len(synced)})", "discord.startup")