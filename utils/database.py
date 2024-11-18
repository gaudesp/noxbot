from typing import Any, Union
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine  # Importer AsyncEngine
from sqlalchemy.engine import Result
from .dotenv import setting

Base = declarative_base()
class Database:
  """Classe utilitaire pour gérer les interactions avec une base de données asynchrone."""

  def __init__(self, db_path: str = 'sqlite+aiosqlite:///:memory:') -> None:
    """
    Initialise la connexion à la base de données.

    :param db_path: Chemin vers la base de données ou URL de connexion.
    :type db_path: str
    """
    self.db_path: str = db_path
    self.engine: AsyncEngine = self._create_engine()
    self.Session: sessionmaker = self._create_session()

  # Public methods

  async def setup(self) -> None:
    """
    Crée toutes les tables définies dans les modèles SQLAlchemy.

    :return: None
    :rtype: None
    """
    async with self.engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

  async def execute(self, query: str) -> Result:
    """
    Exécute une requête SQL et retourne le résultat.

    :param query: Requête SQL à exécuter.
    :type query: str
    :return: Résultat de la requête sous forme de sqlalchemy.engine.Result.
    :rtype: Result
    """
    async with self.Session() as session:
      result: Result = await session.execute(query)
      await session.commit()
      return result

  async def insert(self, entity: Any) -> Any:
    """
    Insère une nouvelle entité dans la base de données.

    :param entity: Instance d'un modèle SQLAlchemy à insérer.
    :type entity: Any
    :return: Entité insérée avec mise à jour de ses champs (par exemple, ID généré).
    :rtype: Any
    """
    async with self.Session() as session:
      session.add(entity)
      await session.commit()
      await session.refresh(entity)
      return entity

  async def delete(self, entities: Union[Any, list[Any]]) -> None:
    """
    Supprime une ou plusieurs entités de la base de données.

    :param entities: Entité ou liste d'entités à supprimer.
    :type entities: Union[Any, list[Any]]
    :return: None
    :rtype: None
    """
    async with self.Session() as session:
      if isinstance(entities, list):
        for entity in entities:
          await session.delete(entity)
      else:
        await session.delete(entities)
      await session.commit()

  async def close(self) -> None:
    """
    Ferme la connexion à la base de données.

    :return: None
    :rtype: None
    """
    await self.engine.dispose()

  # Private methods

  def _create_engine(self) -> AsyncEngine:  # Corriger le type ici pour retourner un AsyncEngine
    """
    Crée le moteur de base de données asynchrone.

    :return: Instance de SQLAlchemy async engine.
    :rtype: AsyncEngine
    """
    return create_async_engine(self.db_path, echo=True)

  def _create_session(self) -> sessionmaker:
    """
    Crée une session asynchrone pour interagir avec la base de données.

    :return: Session asynchrone prête à être utilisée pour les transactions.
    :rtype: sessionmaker
    """
    return sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

database = Database(db_path=setting.get_db_path())
