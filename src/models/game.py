# src/models/game.py
from sqlalchemy import Column, Integer, String, ForeignKey
from config.database import Base

class Game(Base):
  __tablename__ = 'games'

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  channel_id = Column(Integer)
  last_news_id = Column(String, nullable=True)
  guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)

  @property
  def channel(self) -> str:
    """Retourne la mention du canal sous forme de chaîne."""
    return f"<#{self.channel_id}>"

  def to_dict(self) -> dict:
    """Convertit l'objet Game en dictionnaire."""
    return {
      'game_name': self.name,
      'app_id': self.id,
      'channel': self.channel,
    }
