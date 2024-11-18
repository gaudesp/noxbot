from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, autoincrement=True)
  discord_id = Column(String, unique=True, nullable=False)
  username = Column(String, nullable=False)
  disabled = Column(Boolean, default=False)
  subscriptions = relationship("Subscription", backref="user")
