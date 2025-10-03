# backend/src/models/card.py

from pydantic import BaseModel
from typing import Optional

class Card(BaseModel):
    id: int
    name: str
    elixir_cost: int
    rarity: str
    type: str
    arena: Optional[str] = None
    image_url: str
    image_url_evo: Optional[str] = None # For evolved cards
