from collections import defaultdict
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from discord.ext import commands, tasks
from utils.logging import logger
from bot.services.news import NewsService
from models import Game, FollowedGame, News
from utils.discord import DiscordBot, NewsEmbed

log = logger.get_logger(__name__)

class NewsTask(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    self.bot = bot
    self.news_service = NewsService(bot.database)
    self.check_for_news.start()

  @tasks.loop(seconds=1800)
  async def check_for_news(self) -> None:
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
          steam_news_id = await self.news_service.get_news_by_steam_id(game_steam_id, 'id')
          if not steam_news_id:
            continue
            
          game = servers_following_game[0].game
          latest_news = game.news

          if latest_news and steam_news_id.get('steam_id') == latest_news.steam_id:
            continue

          steam_news = await self.news_service.get_news_by_steam_id(game_steam_id)
          steam_news['game_id'] = game.id

          if latest_news:
            await self.bot.database.execute(
              update(News).where(News.id == latest_news.id).values(**steam_news)
            )
          else:
            await self.bot.database.insert(News(**steam_news))

          new_articles.append(steam_news)

          for followed_game in servers_following_game:
            news_embed = NewsEmbed(news=steam_news, game=followed_game.game.to_dict())
            channel = self.bot.get_channel(int(followed_game.discord_channel_id))
            await channel.send(embed=news_embed.create())
        except Exception as e:
          log.error(f"Error processing game {game_steam_id}: {e}")
          continue

      log.info(f"{len(new_articles)} new article(s) found.")
    except Exception as e:
      log.error(f"Unexpected error during news check: {e}")

  @check_for_news.before_loop
  async def before_check_for_news(self) -> None:
    await self.bot.wait_until_ready()

async def setup(bot) -> None:
  await bot.add_cog(NewsTask(bot))
