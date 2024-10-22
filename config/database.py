# config/database.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.schemas.game import GameSchema
from utils.discord import DiscordBot

Base = declarative_base()

class Database:
  def __init__(self, bot: DiscordBot):
    self.engine = create_async_engine(bot.settings.db_path, echo=False)
    self.Session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

  async def setup(self):
    async with self.engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

  async def execute(self, query):
    async with self.Session() as session:
      result = await session.execute(query)
      await session.commit()
      return result

  async def insert(self, entity: GameSchema):
    async with self.Session() as session:
      session.add(entity)
      await session.commit()
      await session.refresh(entity)
      return entity
  
  async def close(self):
    await self.engine.dispose()
