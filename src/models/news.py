from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class News(Base):
  __tablename__ = 'news'
  id = Column(Integer, primary_key=True, autoincrement=True)
  game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
  title = Column(String, nullable=False)
  description = Column(String, nullable=True)
  url = Column(String, nullable=False)
  published_date = Column(DateTime, nullable=False)
  image_url = Column(String, nullable=True)
