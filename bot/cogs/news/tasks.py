from collections import defaultdict
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from discord.ext import commands, tasks
from utils.logging import logger
from bot.services.news import NewsService
from models import Game, FollowedGame, News
from utils.discord import DiscordBot

log = logger.get_logger(__name__)

class NewsTask(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise la tâche pour vérifier les actualités."""
    self.bot = bot
    self.news_service = NewsService(bot.database)
    self.check_for_news.start()

  @tasks.loop(seconds=1800)
  async def check_for_news(self) -> None:
    """
    Vérifie périodiquement s'il y a de nouvelles actualités pour les jeux suivis par les serveurs Discord.
    """
    log.info('Checking Steam news...')
    
    try:
      followed_games = (await self.bot.database.execute(
        select(FollowedGame)
        .options(
          joinedload(FollowedGame.game).joinedload(Game.news),
          joinedload(FollowedGame.server)
        )
      )).scalars().all()

      if not followed_games:
        log.info("No game followed.")
        return

      games_by_steam_id = defaultdict(list)
      for followed_game in followed_games:
        games_by_steam_id[followed_game.game.steam_id].append(followed_game)

      new_articles = []

      for game_steam_id, servers_following_game in games_by_steam_id.items():
        try:
          steam_news = await self.news_service.get_news_by_steam_id(game_steam_id)
          if not steam_news:
            continue

          game = servers_following_game[0].game
          latest_news = game.news

          if latest_news and steam_news.get('steam_id') == latest_news.steam_id:
            continue

          steam_news['game_id'] = game.id
          await self.bot.database.execute(
            update(News).where(News.id == latest_news.id).values(**steam_news)
          )
          new_articles.append(steam_news)

          for following_game in servers_following_game:
            log.info(f"Server n°{following_game.server.discord_id} : {game.name} -> {following_game.channel}")
        except Exception as e:
          log.error(f"Error processing game {game_steam_id}: {e}")
          continue 

      log.info(f"{len(new_articles)} new article(s) found.")
    except Exception as e:
      log.error(f"Unexpected error during news check: {e}")

  @check_for_news.before_loop
  async def before_check_for_news(self) -> None:
    """Attend que le bot soit prêt avant de démarrer la vérification des actualités."""
    await self.bot.wait_until_ready()

async def setup(bot) -> None:
  """Ajoute la tâche de vérification des actualités au bot."""
  await bot.add_cog(NewsTask(bot))
