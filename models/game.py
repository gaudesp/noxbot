from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref, remote
from utils.database import BaseModel

class Game(BaseModel):
  __tablename__ = 'games'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False)
  steam_id = Column(String, unique=True, nullable=False)

  followed_by_servers = relationship("FollowedGame", back_populates="game")
  news = relationship("News", back_populates="game", uselist=False)
