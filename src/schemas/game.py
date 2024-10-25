# src/schemas/game.py
from pydantic import BaseModel
from typing import Optional

class Game(BaseModel):
  id: int
  name: str
  guild_id: int
  channel_id: int
  last_news_id: Optional[str] = None
  channel: str

  class Config:
    """Configuration de Pydantic pour le modèle Game."""
    from_attributes = True
