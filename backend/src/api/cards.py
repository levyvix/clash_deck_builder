# backend/src/api/cards.py

from fastapi import APIRouter, Depends, Response
from typing import List
import logging

from ..models.card import Card
from ..services.card_service import CardService
from ..utils.dependencies import get_card_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cards", response_model=List[Card])
async def get_all_cards(
    response: Response,
    card_service: CardService = Depends(get_card_service)
):
    """
    Fetch all Clash Royale cards from the database.

    Returns cards with appropriate cache headers since card data rarely changes.
    """
    logger.info("Fetching cards from database")
    cards = await card_service.get_all_cards()
    logger.info(f"Successfully retrieved {len(cards)} cards")

    # Add cache headers for client-side caching
    # Cards rarely change, so we can cache for 24 hours
    response.headers["Cache-Control"] = "public, max-age=86400"  # 24 hours
    response.headers["ETag"] = f"cards-{len(cards)}"

    return cards


@router.post("/cards/invalidate-cache")
async def invalidate_cards_cache(card_service: CardService = Depends(get_card_service)):
    """
    Invalidate the card cache.

    This endpoint should be called after card data is updated (e.g., after running ingest_cards.py).
    """
    logger.info("Invalidating card cache")
    card_service.invalidate_cache()
    return {"message": "Card cache invalidated successfully"}


@router.get("/cards/cache-stats")
async def get_cache_stats(card_service: CardService = Depends(get_card_service)):
    """Get card cache statistics for monitoring."""
    stats = card_service.get_cache_stats()
    return stats
