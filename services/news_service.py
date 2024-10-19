# tasks/check_for_news.py
from bs4 import BeautifulSoup
from discord.ext import tasks
from embeds.news_embed import NewsEmbed
import services.steam_api as steam_api
from repositories import game_repository
from utils.logger import logger
import re
from urllib.parse import urlparse

class NewsService:
    def __init__(self, bot):
        self.bot = bot

    async def check_all_news(self):
        games = game_repository.get_all_games()
        for game in games:
            await self.get_last_news(game.app_id, game.guild_id, game.channel_id, game.game_name, game.last_news_id, check_last_news=True)

    async def get_last_news(self, app_id, guild_id, channel_id, game_name, last_news_id, check_last_news=False):
        news = await steam_api.get_game_news(app_id)
        if news and (not check_last_news or news['gid'] != last_news_id):
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await self.send_last_news(news, app_id, guild_id, channel, game_name)
            else:
                logger.log("Le channel spécifié n'existe pas.", "danger")
        else:
            logger.log(f"Aucune nouvelle actualité n'a été trouvée pour le jeu {game_name}")

    async def send_last_news(self, news, app_id, guild_id, channel, game_name):
        contents = news['contents']

        soup = BeautifulSoup(contents, 'html.parser')

        cleaned_contents = soup.get_text(separator=' ', strip=True)

        image_urls = [img['src'] for img in soup.find_all('img')]

        custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', contents)

        image_urls += [url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images') for url in custom_image_urls]

        if image_urls:
          image_url = image_urls[0]  # Utiliser la première image trouvée
        else:
          image_url = await steam_api.get_game_image_url(app_id)

        cleaned_contents = re.sub(r'\[img\].*?\[/img\]', '', cleaned_contents)
        cleaned_contents = re.sub(r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]', '', cleaned_contents)
        cleaned_contents = re.sub(r'\[.*?\]', '', cleaned_contents)
        cleaned_contents = re.sub(r'\s+', ' ', cleaned_contents).strip() 
        cleaned_contents = re.sub(r'^\d+\.\s*', '', cleaned_contents, flags=re.MULTILINE)

        embed = NewsEmbed(
          title=news['title'],
          url=news['url'],
          description=cleaned_contents[:300] + "...",
          game_name=game_name,
          image_url=image_url
        ).create()

        await channel.send(embed=embed)
        logger.log(f"L'actualité n°{news['gid']} a été publiée dans le channel {channel.name}")
        game_repository.update_last_news_id(app_id, guild_id, news['gid'])

    async def update_last_news(self, app_id, guild_id):
        news = await steam_api.get_game_news(app_id)
        game_repository.update_last_news_id(app_id, guild_id, news['gid'])
