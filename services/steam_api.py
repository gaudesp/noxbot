# services/steam_api.py
import aiohttp
from config import STEAM_API_KEY

async def get_game_news(app_id):
    url = f'http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={app_id}&format=json&language=fr'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                news_items = (await response.json()).get('appnews', {}).get('newsitems', [])
                if news_items:
                    for item in news_items:
                        if item.get('feedname') == 'steam_community_announcements':
                            return item 
    return None

async def get_game_image_url(app_id):
    url = f"http://store.steampowered.com/api/appdetails?appids={app_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data and str(app_id) in data and data[str(app_id)]['success']:
                return data[str(app_id)]['data']['header_image']
    return None

async def get_game_name(app_id):
    url = f"http://store.steampowered.com/api/appdetails?appids={app_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data and str(app_id) in data and data[str(app_id)]['success']:
                return data[str(app_id)]['data']['name']
    return None

async def search_game_by_name(game_name):
    url = f"http://api.steampowered.com/ISteamApps/GetAppList/v2/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                app_list = (await response.json()).get('applist', {}).get('apps', [])
                matching_games = [app for app in app_list if game_name.lower() in app['name'].lower()]
                return matching_games[:25] 
    return None
