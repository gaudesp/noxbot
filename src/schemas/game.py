# src/schemas/game_schema.py
from pydantic import BaseModel
from typing import Optional

class GameSchema(BaseModel):
  app_id: int
  guild_id: int
  channel_id: int
  game_name: str
  last_news_id: Optional[str] = None

  class Config:
    from_attributes = True
