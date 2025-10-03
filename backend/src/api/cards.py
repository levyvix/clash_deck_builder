# backend/src/api/cards.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.card import Card
from ..services.clash_api_service import ClashRoyaleAPIService

router = APIRouter()

# Placeholder for dependency injection of ClashRoyaleAPIService
async def get_clash_api_service() -> ClashRoyaleAPIService:
    # In a real app, API key would come from config/env vars
    return ClashRoyaleAPIService(api_key="YOUR_CLASH_ROYALE_API_KEY")

@router.get("/cards", response_model=List[Card])
async def get_all_cards(clash_api: ClashRoyaleAPIService = Depends(get_clash_api_service)):
    try:
        cards_data = await clash_api.get_cards()
        # Convert raw API data to Card models
        # For now, just return empty list as service is placeholder
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cards: {e}")
