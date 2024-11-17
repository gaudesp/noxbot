from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, backref, declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, autoincrement=True)
  discord_id = Column(String, unique=True, nullable=False)
  username = Column(String, nullable=False)
  disabled = Column(Boolean, default=False)
  subscriptions = relationship("Subscription", backref="user")

class Server(Base):
  __tablename__ = 'servers'
  id = Column(Integer, primary_key=True, autoincrement=True)
  discord_id = Column(String, unique=True, nullable=False)
  name = Column(String, nullable=False)
  disabled = Column(Boolean, default=False)
  premium_status = Column(Boolean, default=False)
  premium_expires_at = Column(DateTime, nullable=True)
  subscriptions = relationship("Subscription", backref="server")
  followed_games = relationship("FollowedGame", backref="server")

class Subscription(Base):
  __tablename__ = 'subscriptions'
  id = Column(Integer, primary_key=True, autoincrement=True)
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
  start_date = Column(DateTime, default=datetime.now(timezone.utc))
  end_date = Column(DateTime, nullable=False)

class Game(Base):
  __tablename__ = 'games'
  id = Column(Integer, primary_key=True, autoincrement=True)
  steam_id = Column(String, unique=True, nullable=False)
  name = Column(String, nullable=False)
  news = relationship("News", backref=backref("game"), uselist=False)
  followed_by_servers = relationship("FollowedGame", backref="game")

class FollowedGame(Base):
  __tablename__ = 'followed_games'
  id = Column(Integer, primary_key=True, autoincrement=True)
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
  channel_id = Column(String, nullable=False)
  last_news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
  last_news = relationship("News", backref="followed_games", foreign_keys=[last_news_id])

  @property
  def channel(self) -> str:
    """Retourne la mention du canal sous forme de chaîne."""
    return f"<#{self.channel_id}>"

class News(Base):
  __tablename__ = 'news'
  id = Column(Integer, primary_key=True, autoincrement=True)
  game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
  title = Column(String, nullable=False)
  description = Column(String, nullable=True)
  url = Column(String, nullable=False)
  published_date = Column(DateTime, nullable=False)
  image_url = Column(String, nullable=True)
