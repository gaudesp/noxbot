from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class FollowedGame(Base):
  __tablename__ = 'followed_games'
  id = Column(Integer, primary_key=True, autoincrement=True)
  discord_channel_id = Column(String, nullable=False)
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
  last_news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
  last_news = relationship("News", backref="followed_games", foreign_keys=[last_news_id])

  @property
  def channel(self) -> str:
    """Retourne la mention du canal sous forme de chaîne."""
    return f"<#{self.channel_id}>"
