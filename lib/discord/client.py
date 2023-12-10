import discord
from config import Setting
from lib.logging import Logger
from app.discord.tasks.send_waven_patchnotes import send_waven_patchnotes
from app.discord.hooks.scrape_waven_patchnotes import scrape_waven_patchnotes

setting = Setting()
logger = Logger('client')

class Client():
  def __init__(self):
    self.bot = discord.Client(intents = discord.Intents.all())
    self.on_ready = self.bot.event(self.on_ready)
    self.setup_hook = self.bot.event(self.setup_hook)
  
  async def on_ready(self):
    await self.bot.wait_until_ready()
    logger.log(f"Discord BOT is now online")
    await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Nox Studio"))
    logger.log(f"Discord BOT activity has been updated")
    await self.after_ready()

  async def setup_hook(self):
    logger.log(f"Starting Discord BOT in {setting.BOT_ENV} mode")
    await scrape_waven_patchnotes()
    
  def start(self):
    self.bot.run(setting.DISCORD_TOKEN)
  
  async def after_ready(self):
    await send_waven_patchnotes(self.bot)
