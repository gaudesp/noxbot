from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from utils.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)

    subscriptions = relationship("Subscription", back_populates="user")  # Relation explicite avec `Subscription`

    def __repr__(self):
        return f"<User(id={self.id}, discord_id={self.discord_id}, username={self.username}, disabled={self.disabled})>"
