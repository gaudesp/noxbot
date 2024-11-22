import os
import discord
from datetime import datetime
from discord.ext import commands
from config.setting import setting
from utils.database import Database, database
from utils.logging import logger

log = logger.get_logger(__name__)

class DiscordBot(commands.Bot):
  """
  Classe utilitaire pour gérer un bot Discord.
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
    self.owner_id = setting.discord_owner_id

  async def on_ready(self) -> None:
    """
    Appelé lorsque le bot est prêt.

    :return: None
    """
    log.info(f"{self.user} is online | Server(s) : {len(self.guilds)}")

  async def setup_hook(self) -> None:
    """
    Configuration initiale.

    :return: None
    """
    await self._init_database()
    await self._load_extensions()
    await self._sync_commands()
    log.info("Initial BOT setup completed.")

  async def close(self) -> None:
    """
    Ferme la connexion du bot.

    :return: None
    """
    log.info("Closing BOT...")
    await self.database.close()
    await super().close()

  async def _init_database(self) -> None:
    await self.database.setup()
    log.info("Database connection established")

  async def _load_extensions(self) -> None:
    """
    Charge les extensions.

    :return: None
    """
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
    """
    Synchronise les commandes.

    :return: None
    """
    synced = await self.tree.sync()
    log.info(f"{len(synced)} command(s) synced : {', '.join(command.name for command in synced)}")

class NewsEmbed:
  """
  Gère la création d'un embed Discord pour une actualité.

  :param news: Instance de l'objet News contenant les données nécessaires.
  :param color: Couleur de l'embed (par défaut bleu).
  """
  def __init__(self, news, game, color=discord.Color.blue()) -> None:
    self.news = news
    self.game = game
    self.color = color

  def create(self) -> discord.Embed:
    """
    Crée et renvoie un embed Discord configuré pour l'actualité.

    :return: Embed Discord configuré.
    :rtype: discord.Embed
    """
    embed = discord.Embed(
      title=self.news.title,
      url=self.news.url,
      description=self.news.description,
      color=self.color
    )
    self._add_author(embed)
    self._add_image(embed)
    self._add_footer(embed)
    return embed

  def _add_author(self, embed: discord.Embed) -> None:
    """
    Ajoute l'auteur à l'embed basé sur le nom du jeu.

    :param embed: L'embed à modifier.
    :rtype: None
    """
    if self.game.name:
      embed.set_author(name=self.game.name)

  def _add_image(self, embed: discord.Embed) -> None:
    """
    Ajoute une image principale à l'embed si disponible.

    :param embed: L'embed à modifier.
    :rtype: None
    """
    if self.news.image_url:
      image_url = self.news.image_url
    elif self.game.image_url:
      image_url = self.game.image_url
    else:
      return

    embed.set_image(url=image_url)

  def _add_footer(self, embed: discord.Embed) -> None:
    """
    Ajoute un pied de page avec la date formatée.

    :param embed: L'embed à modifier.
    :rtype: None
    """
    if self.news.published_date:
      formatted_date = self.news.published_date.strftime("%Y-%m-%d %H:%M:%S")
      embed.set_footer(text=f"Published on: {formatted_date}")

bot = DiscordBot()
logger.get_logger("discord")
