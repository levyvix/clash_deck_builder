# backend/src/models/card.py

from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Optional

class Card(BaseModel):
    id: int = Field(..., ge=1, description="Unique card identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Card name")
    elixir_cost: int = Field(..., ge=0, le=10, description="Elixir cost of the card")
    rarity: str = Field(..., description="Card rarity")
    type: str = Field(..., description="Card type")
    arena: Optional[str] = Field(None, max_length=50, description="Arena where card is unlocked")
    image_url: str = Field(..., min_length=1, description="URL to card image")
    image_url_evo: Optional[str] = Field(None, description="URL to evolved card image")

    @field_validator('rarity')
    @classmethod
    def validate_rarity(cls, v):
        """Validate that rarity is one of the allowed values"""
        allowed_rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Champion']
        if v not in allowed_rarities:
            raise ValueError(f'Rarity must be one of {allowed_rarities}, got: {v}')
        return v

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validate that type is one of the allowed values"""
        allowed_types = ['Troop', 'Spell', 'Building']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of {allowed_types}, got: {v}')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate card name is not empty and properly formatted"""
        if not v or not v.strip():
            raise ValueError('Card name cannot be empty')
        return v.strip()

    @field_validator('image_url', 'image_url_evo')
    @classmethod
    def validate_image_urls(cls, v):
        """Validate image URLs are properly formatted"""
        if v is not None and not v.strip():
            raise ValueError('Image URL cannot be empty string')
        return v.strip() if v else v

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 26000000,
                "name": "Knight",
                "elixir_cost": 3,
                "rarity": "Common",
                "type": "Troop",
                "arena": "Training Camp",
                "image_url": "https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png",
                "image_url_evo": None
            }
        }
    )
