from typing import Any, Union
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.engine import Result
from config import config

Base = declarative_base()

class BaseModel(Base):
  __abstract__ = True
  
  def to_dict(self):
    return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Database:
  def __init__(self, db_path: str = 'sqlite+aiosqlite:///:memory:') -> None:
    self.db_path: str = db_path
    self.engine: AsyncEngine = self._create_engine()
    self.Session: sessionmaker = self._create_session()

  async def setup(self) -> None:
    async with self.engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

  async def execute(self, query: str) -> Result:
    async with self.Session() as session:
      result: Result = await session.execute(query)
      await session.commit()
      return result

  async def insert(self, entity: Any) -> Any:
    async with self.Session() as session:
      session.add(entity)
      await session.commit()
      await session.refresh(entity)
      return entity

  async def delete(self, entities: Union[Any, list[Any]]) -> None:
    async with self.Session() as session:
      if isinstance(entities, list):
        for entity in entities:
          await session.delete(entity)
      else:
        await session.delete(entities)
      await session.commit()

  async def close(self) -> None:
    await self.engine.dispose()

  def _create_engine(self) -> AsyncEngine:
    return create_async_engine(self.db_path, echo=False)

  def _create_session(self) -> sessionmaker:
    return sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

database = Database(db_path=config.db_path)
