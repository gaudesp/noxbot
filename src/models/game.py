from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref, declarative_base

Base = declarative_base()

class Game(Base):
  __tablename__ = 'games'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False)
  steam_id = Column(String, unique=True, nullable=False)
  news = relationship("News", backref=backref("game"), uselist=False)
  followed_by_servers = relationship("FollowedGame", backref="game")
