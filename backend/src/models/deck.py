# backend/src/models/deck.py

from pydantic import BaseModel
from typing import List, Optional
from .card import Card

class Deck(BaseModel):
    id: Optional[int] = None
    name: str
    user_id: Optional[int] = None
    cards: List[Card]
    evolution_slots: List[Card]
    average_elixir: float
