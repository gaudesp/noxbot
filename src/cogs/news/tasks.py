from collections import defaultdict
import discord
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, subqueryload
from services.news import NewsService
from src.models import Game, FollowedGame, Server, News
from discord.ext import commands, tasks
from utils.discord import DiscordBot
from utils.formatting import SteamFormatter
from utils.steamer import steam
from utils.logging import logger

log = logger.get_logger(__name__)

class NewsTask(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot
    self.news_service = NewsService(bot.database)
    self.check_for_news.start()

  @tasks.loop(seconds=1800)
  async def check_for_news(self) -> None:
    """
    Vérifie toutes les demi-heures s'il y a des nouvelles actualités disponibles pour les jeux suivis par les serveurs Discord.
    """
    log.info('Début de la vérification des actualités...')
    
    # Liste des actualités à envoyer aux serveurs
    news_to_send = []

    # Recherche tous les jeux suivis de tous les serveurs
    find_followed_games = await self.bot.database.execute(
      select(FollowedGame)
      .options(
        joinedload(FollowedGame.game).joinedload(Game.news),
        joinedload(FollowedGame.server)
      )
    )

    # Récupère tous les jeux suivis
    followed_games = find_followed_games.scalars().all()
    if not followed_games:
      log.info('Aucun jeu suivi trouvé.')
      return

    # Regroupe les jeux par leur steam_id pour éviter de multiples appels API
    games_by_steam_id = defaultdict(list)
    for followed_game in followed_games:
      games_by_steam_id[followed_game.game.steam_id].append(followed_game)

    # Parcours chaque jeu par steam_id
    news_to_process = []
    for game_steam_id, followed_games_by_servers in games_by_steam_id.items():
      news_dict = self.news_service.get_news_by_steam_id(game_steam_id)
      if not news_dict:
        continue
      
      game: Game = followed_games_by_servers.pop(0).game
      news_to_process.append(news_dict.update({'game_id': game.id}))
      # # Parcours chaque jeu suivi par serveur
      # for followed_game in followed_games_by_servers:
      #   if news_dict.get('steam_id') != followed_game.game.news.steam_id:
      #     # Nouvelle actualité

          
      #     # Aucune actualité précédente, on crée une nouvelle actualité
      #     new_news = News(**news_dict, game_id=followed_game.game.id)
      #     new_news = await self.bot.database.insert(new_news)
      #     log.info(f"Nouvelle actualité créée : {new_news.to_dict()}.")
      #     news_to_send.append(new_news)
      #   elif news_for_game.get('gid') != existing_news.steam_id:
      #     # Actualité existante mais différente, mise à jour
      #     updated_news = await self.bot.database.execute(
      #       update(News).where(News.id == existing_news.id).values(**news_dict)
      #     )
      #     log.info(f"Actualité mise à jour : {updated_news.to_dict()}.")
      #     news_to_send.append(updated_news)
      #   else:
      #     log.info("L'actualité est déjà à jour.")

    # Log des actualités à envoyer
    log.info(f"{len(news_to_send)} actualités à envoyer.")
    for news in news_to_send:
      log.info(f"Actualité prête à être envoyée : {news.to_dict()}.")

  @check_for_news.before_loop
  async def before_check_for_news(self) -> None:
    """Attend que le bot soit prêt avant de démarrer la vérification des actualités."""
    await self.bot.wait_until_ready()

async def setup(bot: DiscordBot) -> None:
  await bot.add_cog(NewsTask(bot))
