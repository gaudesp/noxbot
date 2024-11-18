from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Subscription(Base):
  __tablename__ = 'subscriptions'
  id = Column(Integer, primary_key=True, autoincrement=True)
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
  start_date = Column(DateTime, default=datetime.now(timezone.utc))
  end_date = Column(DateTime, nullable=False)
