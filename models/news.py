from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from utils.database import BaseModel

class News(BaseModel):
  __tablename__ = 'news'
  id = Column(Integer, primary_key=True, autoincrement=True)
  title = Column(String, nullable=False)
  description = Column(String, nullable=True)
  steam_id = Column(String, unique=True, nullable=False)
  url = Column(String, nullable=False)
  published_date = Column(DateTime, nullable=False)
  image_url = Column(String, nullable=True)
  
  game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
  game = relationship("Game", back_populates="news")
