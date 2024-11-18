import discord
from datetime import datetime
from discord.ext import commands
from .database import Database, database
from .logging import logger

log = logger.get_logger(__name__)

class DiscordBot(commands.Bot):
  """
  Classe utilitaire pour gérer un bot Discord.
  Fournit les événements de base : démarrage, fermeture, et préparation initiale.
  """

  database: Database = database
  uptime: datetime = datetime.now()

  def __init__(self, **kwargs) -> None:
    """
    Initialise le bot Discord avec des paramètres par défaut.

    :param kwargs: Paramètres optionnels pour la configuration du bot.
    """
    kwargs.setdefault("activity", discord.Activity(type=discord.ActivityType.listening, name="NOKX"))
    kwargs.setdefault("allowed_mentions", discord.AllowedMentions(everyone=False))
    kwargs.setdefault("case_insensitive", True)
    kwargs.setdefault("intents", discord.Intents.all())
    kwargs.setdefault("max_messages", 2500)
    kwargs.setdefault("status", discord.Status.online)
    super().__init__(command_prefix='/', **kwargs)

  async def on_ready(self) -> None:
    """
    Appelé lorsque le bot est prêt et connecté à Discord.

    :return: None
    """
    log.info(f"{self.user} is online | Servers : {len(self.guilds)}")

  async def setup_hook(self) -> None:
    """
    Configuration initiale avant de commencer à écouter les événements.

    :return: None
    """
    await self.database.setup()
    log.info("Initial BOT setup completed.")

  async def close(self) -> None:
    """
    Ferme la connexion du bot.

    :return: None
    """
    log.info("Closing BOT...")
    await self.database.close()
    await super().close()

bot = DiscordBot()
logger.get_logger("discord")
