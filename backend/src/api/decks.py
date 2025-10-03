# backend/src/api/decks.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.deck import Deck
from ..models.user import User
from ..services.deck_service import DeckService

router = APIRouter()

# Placeholder for dependency injection of DeckService
async def get_deck_service() -> DeckService:
    # In a real app, db_connection would come from config/env vars
    return DeckService(db_connection=None) # Placeholder

# Placeholder for dependency injection of current user
async def get_current_user() -> User:
    # In a real app, this would handle authentication and return the current user
    return User(id=1) # Simulate a logged-in user

@router.post("/decks", response_model=Deck)
async def create_user_deck(
    deck: Deck,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    try:
        created_deck = await deck_service.create_deck(deck, current_user)
        return created_deck
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create deck: {e}")

@router.get("/decks", response_model=List[Deck])
async def get_all_user_decks(
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    try:
        decks = await deck_service.get_user_decks(current_user)
        return decks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve decks: {e}")

@router.get("/decks/{deck_id}", response_model=Deck)
async def get_single_user_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    try:
        deck = await deck_service.get_deck(deck_id, current_user)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        return deck
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve deck: {e}")

@router.put("/decks/{deck_id}", response_model=Deck)
async def update_single_user_deck(
    deck_id: int,
    deck: Deck,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    try:
        updated_deck = await deck_service.update_deck(deck, current_user)
        if not updated_deck:
            raise HTTPException(status_code=404, detail="Deck not found or not authorized")
        return updated_deck
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update deck: {e}")

@router.delete("/decks/{deck_id}", status_code=204)
async def delete_single_user_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    try:
        success = await deck_service.delete_deck(deck_id, current_user)
        if not success:
            raise HTTPException(status_code=404, detail="Deck not found or not authorized")
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete deck: {e}")
