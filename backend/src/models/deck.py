# backend/src/models/deck.py

from pydantic import BaseModel, validator, Field, root_validator
from typing import List, Optional
from .card import Card


class Deck(BaseModel):
    id: Optional[int] = Field(None, ge=1, description="Unique deck identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Deck name")
    user_id: Optional[int] = Field(None, ge=1, description="User who owns this deck")
    cards: List[Card] = Field(..., description="List of cards in the deck")
    evolution_slots: List[Card] = Field(
        default_factory=list, description="Evolution card slots"
    )
    average_elixir: Optional[float] = Field(
        None, ge=0, le=10, description="Average elixir cost of the deck"
    )

    @validator("name")
    def validate_name(cls, v):
        """Validate deck name is not empty and properly formatted"""
        if not v or not v.strip():
            raise ValueError("Deck name cannot be empty")
        return v.strip()

    @validator("cards")
    def validate_cards_count(cls, v):
        """Validate that deck has exactly 8 cards"""
        if len(v) != 8:
            raise ValueError(f"Deck must have exactly 8 cards, got {len(v)}")
        return v

    @validator("evolution_slots")
    def validate_evolution_slots(cls, v):
        """Validate that deck has at most 2 evolution slots"""
        if len(v) > 2:
            raise ValueError(
                f"Deck cannot have more than 2 evolution slots, got {len(v)}"
            )
        return v

    @root_validator
    def validate_evolution_cards_in_deck(cls, values):
        """Validate that evolution slot cards are also in the main deck"""
        cards = values.get("cards", [])
        evolution_slots = values.get("evolution_slots", [])

        if not cards or not evolution_slots:
            return values

        # Get card IDs from main deck
        main_deck_card_ids = {card.id for card in cards}

        # Check that all evolution slot cards are in the main deck
        for evo_card in evolution_slots:
            if evo_card.id not in main_deck_card_ids:
                raise ValueError(
                    f'Evolution slot card "{evo_card.name}" must also be in the main deck'
                )

        return values

    def calculate_average_elixir(self) -> float:
        """Calculate the average elixir cost of the deck including evolution slots"""
        if not self.cards:
            return 0.0

        # Calculate total elixir from main deck cards
        total_elixir = sum(card.elixir_cost for card in self.cards)
        total_cards = len(self.cards)

        # Add evolution slots to the calculation
        # Evolution slots don't add to card count but do add elixir cost
        if self.evolution_slots:
            total_elixir += sum(card.elixir_cost for card in self.evolution_slots)
            # Evolution slots are considered as additional elixir cost for the same cards
            # So we don't increase the card count, but we do increase total elixir

        return round(total_elixir / total_cards, 2) if total_cards > 0 else 0.0

    @root_validator
    def auto_calculate_average_elixir(cls, values):
        """Automatically calculate average elixir if not provided"""
        cards = values.get("cards", [])
        evolution_slots = values.get("evolution_slots", [])
        average_elixir = values.get("average_elixir")

        # If average_elixir is not provided or is None, calculate it
        if average_elixir is None and cards:
            total_elixir = sum(card.elixir_cost for card in cards)
            total_cards = len(cards)

            # Add evolution slots elixir cost
            if evolution_slots:
                total_elixir += sum(card.elixir_cost for card in evolution_slots)

            values["average_elixir"] = (
                round(total_elixir / total_cards, 2) if total_cards > 0 else 0.0
            )

        return values

    def update_average_elixir(self) -> None:
        """Update the average elixir cost of the deck"""
        self.average_elixir = self.calculate_average_elixir()

    class Config:
        """Pydantic configuration"""

        validate_assignment = True
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "My Awesome Deck",
                "user_id": 1,
                "cards": [
                    {
                        "id": 26000000,
                        "name": "Knight",
                        "elixir_cost": 3,
                        "rarity": "Common",
                        "type": "Troop",
                        "arena": "Training Camp",
                        "image_url": "https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png",
                        "image_url_evo": None,
                    }
                ],
                "evolution_slots": [],
                "average_elixir": 3.5,
            }
        }
