# src/schemas/game.py
from pydantic import BaseModel
from typing import Optional, List
from src.schemas.game import Game

class Guild(BaseModel):
  id: int
  name: str
  locale: Optional[str] = 'en'
  games: Optional[List[Game]] = []

  class Config:
    """Configuration de Pydantic pour le modèle Guild."""
    from_attributes = True
