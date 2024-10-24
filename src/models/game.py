# src/models/game.py
from sqlalchemy import Column, Integer, String
from config.database import Base

class Game(Base):
  __tablename__ = 'games'

  app_id = Column(Integer, primary_key=True)
  guild_id = Column(Integer, primary_key=True)
  channel_id = Column(Integer, nullable=False)
  game_name = Column(String)
  last_news_id = Column(String)

  @property
  def channel(self) -> str:
    """Retourne une représentation du canal associé à ce jeu."""
    return f"<#{self.channel_id}>"

  def __repr__(self) -> str:
    """Retourne une représentation de l'objet Game."""
    return f"<Game(app_id={self.app_id}, guild_id={self.guild_id}, channel_id={self.channel_id}, game_name={self.game_name}, last_news_id={self.last_news_id})>"
