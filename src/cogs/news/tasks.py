from collections import defaultdict
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from discord.ext import commands, tasks
from utils.logging import logger
from src.services.news import NewsService
from src.models import Game, FollowedGame, News

log = logger.get_logger(__name__)

class NewsTask(commands.Cog):
  def __init__(self, bot) -> None:
    """Initialise la tâche pour vérifier les actualités."""
    self.bot = bot
    self.news_service = NewsService(bot.database)
    self.check_for_news.start()

  @tasks.loop(seconds=1800)
  async def check_for_news(self) -> None:
    """
    Vérifie toutes les demi-heures s'il y a de nouvelles actualités pour les jeux suivis par les serveurs Discord.
    """
    log.info('Début de la vérification des actualités...')
    
    # Récupérer les jeux suivis avec leurs actualités et serveurs
    followed_games = (await self.bot.database.execute(
      select(FollowedGame)
      .options(
        joinedload(FollowedGame.game).joinedload(Game.news),
        joinedload(FollowedGame.server)
      )
    )).scalars().all()

    if not followed_games:
      log.info("Aucun jeu suivi.")
      return

    news_to_send = []
    games_by_steam_id = defaultdict(list)

    # Grouper les jeux suivis par steam_id
    for fg in followed_games:
      games_by_steam_id[fg.game.steam_id].append(fg)

    # Parcourir chaque steam_id pour vérifier les actualités
    for steam_id, servers_following_game in games_by_steam_id.items():
      steam_news = await self.news_service.get_news_by_steam_id(steam_id)
      if not steam_news:
        continue

      # Récupérer le jeu depuis la base de données
      game = (await self.bot.database.execute(
        select(Game).options(joinedload(Game.news)).where(Game.steam_id == steam_id)
      )).scalar_one_or_none()

      if not game or not game.news:
        continue

      # Si l'actualité est déjà enregistrée, on ignore
      if steam_news.get('steam_id') == game.news.steam_id:
        continue

      # Mise à jour de l'actualité dans la base de données
      steam_news['game_id'] = game.id
      await self.bot.database.execute(
        update(News).where(News.id == game.news.id).values(**steam_news)
      )
      
      # Ajouter aux actualités à envoyer
      news_to_send.extend(servers_following_game)

    log.info(f"{len(news_to_send)} actualités à envoyer.")

    # Envoyer les actualités à chaque serveur
    for followed_game in news_to_send:
      log.info(f"Envoi de l'actualité : {followed_game.to_dict()}")

  @check_for_news.before_loop
  async def before_check_for_news(self) -> None:
    """Attend que le bot soit prêt avant de démarrer la vérification des actualités."""
    await self.bot.wait_until_ready()

async def setup(bot) -> None:
  """Ajoute la tâche de vérification des actualités au bot."""
  await bot.add_cog(NewsTask(bot))
