from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from utils.database import Base

class Server(Base):
  __tablename__ = 'servers'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False)
  discord_id = Column(String, unique=True, nullable=False)
  disabled = Column(Boolean, default=False)
  premium_status = Column(Boolean, default=False)
  premium_expires_at = Column(DateTime, nullable=True)
  subscriptions = relationship("Subscription", backref="server")
  followed_games = relationship("FollowedGame", backref="server")

  def __repr__(self):
    return f"<Server(id={self.id}, name={self.name}, discord_id={self.discord_id})>"
