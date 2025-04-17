from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timezone
from utils.database import BaseModel

class Subscription(BaseModel):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=False)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    server = relationship("Server", back_populates="subscriptions")
    user = relationship("User", back_populates="subscriptions")
