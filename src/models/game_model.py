# src/models/game_model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GameModel(Base):
  __tablename__ = 'games'

  app_id = Column(Integer, primary_key=True)
  guild_id = Column(Integer, primary_key=True)
  channel_id = Column(Integer, nullable=False)
  game_name = Column(String)
  last_news_id = Column(String)

  @property
  def channel(self):
    return f"<#{self.channel_id}>"

  def __repr__(self):
    return f"<Game(app_id={self.app_id}, guild_id={self.guild_id}, channel_id={self.channel_id}, game_name={self.game_name}, last_news_id={self.last_news_id})>"
