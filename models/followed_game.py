from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import BaseModel

class FollowedGame(BaseModel):
  __tablename__ = 'followed_games'
  id = Column(Integer, primary_key=True, autoincrement=True)
  discord_channel_id = Column(String, nullable=False)

  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
  game = relationship("Game", back_populates="followed_by_servers")
  server = relationship("Server", back_populates="followed_games")

  @property
  def channel(self) -> str:
    return f"<#{self.discord_channel_id}>"
