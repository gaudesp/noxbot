from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timezone
from utils.database import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=False)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    server = relationship("Server", back_populates="subscriptions")  # Relation explicite avec `Server`
    user = relationship("User", back_populates="subscriptions")  # Relation explicite avec `User`

    def __repr__(self):
        return f"<Subscription(id={self.id}, start_date={self.start_date}, end_date={self.end_date}, server_id={self.server_id}, user_id={self.user_id})>"
