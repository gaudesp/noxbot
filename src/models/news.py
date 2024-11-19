from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from utils.database import Base

class News(Base):
  __tablename__ = 'news'
  id = Column(Integer, primary_key=True, autoincrement=True)
  title = Column(String, nullable=False)
  description = Column(String, nullable=True)
  url = Column(String, nullable=False)
  published_date = Column(DateTime, nullable=False)
  image_url = Column(String, nullable=True)
  game_id = Column(Integer, ForeignKey('games.id'), nullable=False)

  def __repr__(self):
    return f"<News(id={self.id}, title={self.title}, game_id={self.game_id})>"
