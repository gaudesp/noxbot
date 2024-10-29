# src/repositories/guild.py
from sqlalchemy import update
from sqlalchemy.future import select
from src.schemas.guild import Guild
from src.models.guild import Guild as GuildModel

class GuildRepository:
  def __init__(self, bot) -> None:
    """Initialise le dépôt de guildes avec le bot Discord."""
    self.bot = bot

  async def create_one(self, guild_id: int, guild_name: str) -> Guild:
    """Crée une nouvelle guilde et l'insère dans la base de données."""
    guild = GuildModel(id=guild_id, name=guild_name)
    return await self.bot.database.insert(guild)

  async def get_one_by_guild(self, guild_id: int) -> Guild | None:
    """Récupère une guilde par son identifiant."""
    guild = await self.bot.database.execute(select(GuildModel).where(GuildModel.id == guild_id))
    return guild.scalar_one_or_none()

  async def get_all(self) -> list[GuildModel]:
    """Récupère toutes les guildes de la base de données."""
    games = await self.bot.database.execute(select(GuildModel))
    return games.scalars().all()

  async def update_one(self, guild: Guild, values: dict) -> bool:
    """Met à jour une guilde avec les valeurs fournies."""
    await self.bot.database.execute(update(GuildModel).where(GuildModel.id == guild.id).values(**values))
    return True

  async def delete_one_or_many(self, guild: Guild | list[Guild]) -> bool:
    """Supprime une ou plusieurs guildes de la base de données."""
    await self.bot.database.delete(guild)
    return True
