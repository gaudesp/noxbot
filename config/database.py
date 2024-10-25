# config/database.py
from typing import Any
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.engine import Result

Base = declarative_base()

class Database:
  def __init__(self, db_path: str) -> None:
    """Initialise la base de données avec le chemin spécifié."""
    self.engine = create_async_engine(db_path, echo=False)
    self.Session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

  async def setup(self) -> None:
    """Configure la base de données en créant toutes les tables définies dans le modèle."""
    async with self.engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

  async def execute(self, query) -> Result:
    """Exécute une requête SQL et renvoie le résultat."""
    async with self.Session() as session:
      result = await session.execute(query)
      await session.commit()
      return result

  async def insert(self, entity: Any) -> Any:
    """Insère une nouvelle entité dans la base de données et renvoie l'entité insérée."""
    async with self.Session() as session:
      session.add(entity)
      await session.commit()
      await session.refresh(entity)
      return entity

  async def delete(self, entities: Any) -> None:
    """Supprime une ou plusieurs entités de la base de données."""
    async with self.Session() as session:
      if isinstance(entities, list):
        for entity in entities:
          await session.delete(entity)
      else:
        await session.delete(entities)
      await session.commit()

  async def close(self) -> None:
    """Ferme la connexion à la base de données."""
    await self.engine.dispose()
