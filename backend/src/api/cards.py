# backend/src/api/cards.py

from fastapi import APIRouter, Depends
from typing import List
import logging

from ..models.card import Card
from ..services.card_service import CardService
from ..utils.dependencies import get_card_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cards", response_model=List[Card])
async def get_all_cards(card_service: CardService = Depends(get_card_service)):
    """Fetch all Clash Royale cards from the database."""
    logger.info("Fetching cards from database")
    cards = await card_service.get_all_cards()
    logger.info(f"Successfully retrieved {len(cards)} cards from database")
    return cards
