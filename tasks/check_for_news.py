# tasks/check_for_news.py
from discord.ext import tasks
from config import CHECK_INTERVAL
from services.news_service import NewsService
from utils.logger import logger

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_for_news(bot):
  await NewsService(bot).get_all_news()
  logger.log("Les actualités Steam ont été vérifiées")
