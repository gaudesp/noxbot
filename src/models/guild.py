# src/models/guild.py
from sqlalchemy import Boolean, Column, Integer, String
from config.database import Base
from sqlalchemy.orm import relationship

class Guild(Base):
  __tablename__ = 'guilds'

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  locale = Column(String, default='en')

  games = relationship("Game", backref="guild", cascade="all, delete-orphan")
