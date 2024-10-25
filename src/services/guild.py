# src/services/guild.py
from src.repositories.guild import GuildRepository
from src.models.guild import Guild as GuildModel
from src.utils.discord import DiscordBot

class GuildService:
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le service de guilde avec le bot Discord."""
    self.bot = bot
    self.guild_repository = GuildRepository(bot)

  async def add_guild(self, guild_id: int, guild_name: str) -> GuildModel:
    """Ajoute une nouvelle guilde."""
    guild = await self.guild_repository.create_one(guild_id, guild_name)
    return guild

  async def find_guild(self, guild_id: int) -> GuildModel | None:
    """Récupère une guilde par son identifiant."""
    guild = await self.guild_repository.get_one_by_guild(guild_id)
    return guild

  async def update_guild_locale(self, guild_id: int, locale: str) -> bool:
    """Met à jour la locale d'une guilde."""
    guild = await self.find_guild(guild_id)
    if guild:
      await self.guild_repository.update_one(guild, {"locale": locale})
      return True
    return False

  async def delete_guild(self, guild_id: int) -> GuildModel | bool:
    """Supprime une guilde par son identifiant."""
    guild = await self.find_guild(guild_id)
    if guild:
      await self.guild_repository.delete_one_or_many(guild)
      return guild
    return False
