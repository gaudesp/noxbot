# config/database.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.schemas.game import GameSchema
from sqlalchemy.engine import Result

Base = declarative_base()

class Database:
  def __init__(self, db_path: str) -> None:
    self.engine = create_async_engine(db_path, echo=False)
    self.Session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

  async def setup(self) -> None:
    """Crée les tables dans la base de données."""
    async with self.engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

  async def execute(self, query) -> Result:
    """Exécute une requête SQL et retourne le résultat."""
    async with self.Session() as session:
      result = await session.execute(query)
      await session.commit()
      return result

  async def insert(self, entity: GameSchema) -> GameSchema:
    """Insère un nouvel enregistrement dans la base de données et retourne l'entité insérée."""
    async with self.Session() as session:
      session.add(entity)
      await session.commit()
      await session.refresh(entity)
      return entity
  
  async def close(self) -> None:
    """Ferme la connexion à la base de données."""
    await self.engine.dispose()
