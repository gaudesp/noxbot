from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from utils.database import BaseModel

class Server(BaseModel):
  __tablename__ = 'servers'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False)
  discord_id = Column(String, unique=True, nullable=False)
  disabled = Column(Boolean, default=False)
  premium_status = Column(Boolean, default=False)
  premium_expires_at = Column(DateTime, nullable=True)

  subscriptions = relationship("Subscription", back_populates="server")
  followed_games = relationship("FollowedGame", back_populates="server")
