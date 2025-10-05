# backend/src/api/decks.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging
from datetime import datetime

from ..models.deck import Deck
from ..models.user import User
from ..services.deck_service import DeckService
from ..utils.dependencies import get_deck_service
from ..middleware.auth_middleware import require_auth
from ..exceptions import (
    DatabaseError,
    DeckNotFoundError,
    SerializationError,
    DeckLimitExceededError,
    DeckValidationError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_current_user(user_data: Dict[str, Any] = Depends(require_auth)) -> User:
    """Convert authenticated user data to User model."""
    return User(
        id=user_data["user_id"],
        google_id=user_data["google_id"],
        email=user_data["email"],
        name=user_data["name"],
        avatar=user_data.get("avatar"),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.post("/decks", response_model=Deck, status_code=201)
async def create_user_deck(
    deck: Deck, current_user: User = Depends(get_current_user), deck_service: DeckService = Depends(get_deck_service)
):
    """Create a new deck for the authenticated user."""
    logger.info(f"Creating deck '{deck.name}' for user {current_user.id}")
    created_deck = await deck_service.create_deck(deck, current_user)
    logger.info(f"Successfully created deck {created_deck.id} for user {current_user.id}")
    return created_deck


@router.get("/decks", response_model=List[Deck])
async def get_all_user_decks(
    current_user: User = Depends(get_current_user), deck_service: DeckService = Depends(get_deck_service)
):
    """Retrieve all decks for the authenticated user."""
    logger.info(f"Retrieving all decks for user {current_user.id}")
    decks = await deck_service.get_user_decks(current_user)
    logger.info(f"Retrieved {len(decks)} decks for user {current_user.id}")
    return decks


@router.get("/decks/{deck_id}", response_model=Deck)
async def get_single_user_deck(
    deck_id: int, current_user: User = Depends(get_current_user), deck_service: DeckService = Depends(get_deck_service)
):
    """Retrieve a specific deck by ID for the authenticated user."""
    logger.info(f"Retrieving deck {deck_id} for user {current_user.id}")
    deck = await deck_service.get_deck(deck_id, current_user)

    if not deck:
        logger.warning(f"Deck {deck_id} not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail=f"Deck with ID {deck_id} not found")

    logger.info(f"Successfully retrieved deck {deck_id} for user {current_user.id}")
    return deck


@router.put("/decks/{deck_id}", response_model=Deck)
async def update_single_user_deck(
    deck_id: int,
    deck: Deck,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service),
):
    """Update an existing deck for the authenticated user."""
    deck.id = deck_id
    logger.info(f"Updating deck {deck_id} for user {current_user.id}")
    updated_deck = await deck_service.update_deck(deck, current_user)

    if not updated_deck:
        logger.warning(f"Deck {deck_id} not found for update by user {current_user.id}")
        raise HTTPException(status_code=404, detail=f"Deck with ID {deck_id} not found or not authorized")

    logger.info(f"Successfully updated deck {deck_id} for user {current_user.id}")
    return updated_deck


@router.delete("/decks/{deck_id}", status_code=204)
async def delete_single_user_deck(
    deck_id: int, current_user: User = Depends(get_current_user), deck_service: DeckService = Depends(get_deck_service)
):
    """Delete a deck for the authenticated user."""
    logger.info(f"Deleting deck {deck_id} for user {current_user.id}")
    success = await deck_service.delete_deck(deck_id, current_user)

    if not success:
        logger.warning(f"Deck {deck_id} not found for deletion by user {current_user.id}")
        raise HTTPException(status_code=404, detail=f"Deck with ID {deck_id} not found or not authorized")

    logger.info(f"Successfully deleted deck {deck_id} for user {current_user.id}")
