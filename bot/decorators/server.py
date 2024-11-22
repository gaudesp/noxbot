from functools import wraps
import discord
from sqlalchemy.future import select
from models import Server

def ensure_server(func):
  @wraps(func)
  async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
    find_server = await self.bot.database.execute(select(Server).where(Server.discord_id == interaction.guild.id))
    server = find_server.scalar_one_or_none()
    
    if not server:
      server = await self.bot.database.insert(Server(name=interaction.guild.name, discord_id=interaction.guild.id))

    self.server = server
    return await func(self, interaction, *args, **kwargs)
  
  return wrapper
