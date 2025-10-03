# backend/src/api/decks.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging

from ..models.deck import Deck
from ..models.user import User
from ..services.deck_service import DeckService
from ..utils.dependencies import get_deck_service
from ..exceptions import (
    DatabaseError,
    DeckNotFoundError,
    SerializationError,
    DeckLimitExceededError,
    DeckValidationError
)

logger = logging.getLogger(__name__)
router = APIRouter()


# Placeholder for dependency injection of current user
# TODO: Replace with proper authentication system
async def get_current_user() -> User:
    """
    Placeholder dependency for current user authentication.
    In a real application, this would validate JWT tokens or session cookies.
    """
    return User(id=1)  # Simulate a logged-in user


@router.post("/decks", response_model=Deck, status_code=201)
async def create_user_deck(
    deck: Deck,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    """
    Create a new deck for the authenticated user.
    
    Args:
        deck: Deck data to create
        current_user: Authenticated user (injected)
        deck_service: Deck service instance (injected)
        
    Returns:
        Deck: The created deck with assigned ID
        
    Raises:
        HTTPException:
            - 400 Bad Request: Invalid deck data or validation errors
            - 409 Conflict: User has reached maximum deck limit (20 decks)
            - 500 Internal Server Error: Database or unexpected errors
    """
    try:
        logger.info(f"Creating deck '{deck.name}' for user {current_user.id}")
        created_deck = await deck_service.create_deck(deck, current_user)
        logger.info(f"Successfully created deck {created_deck.id} for user {current_user.id}")
        return created_deck
        
    except DeckLimitExceededError as e:
        logger.warning(f"Deck limit exceeded for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=409,
            detail=f"Maximum deck limit of {e.max_decks} reached. Please delete a deck before creating a new one."
        )
        
    except (DeckValidationError, SerializationError) as e:
        logger.warning(f"Validation error creating deck for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid deck data: {str(e)}"
        )
        
    except DatabaseError as e:
        logger.error(f"Database error creating deck for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create deck due to database error"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error creating deck for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while creating the deck"
        )


@router.get("/decks", response_model=List[Deck])
async def get_all_user_decks(
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    """
    Retrieve all decks for the authenticated user.
    
    Args:
        current_user: Authenticated user (injected)
        deck_service: Deck service instance (injected)
        
    Returns:
        List[Deck]: List of user's decks, ordered by creation date (newest first)
        
    Raises:
        HTTPException:
            - 500 Internal Server Error: Database or unexpected errors
    """
    try:
        logger.info(f"Retrieving all decks for user {current_user.id}")
        decks = await deck_service.get_user_decks(current_user)
        logger.info(f"Retrieved {len(decks)} decks for user {current_user.id}")
        return decks
        
    except DatabaseError as e:
        logger.error(f"Database error retrieving decks for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve decks due to database error"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving decks for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving decks"
        )


@router.get("/decks/{deck_id}", response_model=Deck)
async def get_single_user_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    """
    Retrieve a specific deck by ID for the authenticated user.
    
    Args:
        deck_id: ID of the deck to retrieve
        current_user: Authenticated user (injected)
        deck_service: Deck service instance (injected)
        
    Returns:
        Deck: The requested deck
        
    Raises:
        HTTPException:
            - 404 Not Found: Deck not found or doesn't belong to user
            - 500 Internal Server Error: Database or unexpected errors
    """
    try:
        logger.info(f"Retrieving deck {deck_id} for user {current_user.id}")
        deck = await deck_service.get_deck(deck_id, current_user)
        
        if not deck:
            logger.warning(f"Deck {deck_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=404,
                detail=f"Deck with ID {deck_id} not found"
            )
            
        logger.info(f"Successfully retrieved deck {deck_id} for user {current_user.id}")
        return deck
        
    except DeckNotFoundError:
        logger.warning(f"Deck {deck_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=404,
            detail=f"Deck with ID {deck_id} not found"
        )
        
    except SerializationError as e:
        logger.error(f"Serialization error retrieving deck {deck_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Deck data is corrupted and cannot be retrieved"
        )
        
    except DatabaseError as e:
        logger.error(f"Database error retrieving deck {deck_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve deck due to database error"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving deck {deck_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving the deck"
        )


@router.put("/decks/{deck_id}", response_model=Deck)
async def update_single_user_deck(
    deck_id: int,
    deck: Deck,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    """
    Update an existing deck for the authenticated user.
    
    Args:
        deck_id: ID of the deck to update
        deck: Updated deck data
        current_user: Authenticated user (injected)
        deck_service: Deck service instance (injected)
        
    Returns:
        Deck: The updated deck
        
    Raises:
        HTTPException:
            - 400 Bad Request: Invalid deck data or validation errors
            - 404 Not Found: Deck not found or doesn't belong to user
            - 500 Internal Server Error: Database or unexpected errors
    """
    try:
        # Ensure the deck ID in the URL matches the deck object
        deck.id = deck_id
        
        logger.info(f"Updating deck {deck_id} for user {current_user.id}")
        updated_deck = await deck_service.update_deck(deck, current_user)
        
        if not updated_deck:
            logger.warning(f"Deck {deck_id} not found for update by user {current_user.id}")
            raise HTTPException(
                status_code=404,
                detail=f"Deck with ID {deck_id} not found or not authorized"
            )
            
        logger.info(f"Successfully updated deck {deck_id} for user {current_user.id}")
        return updated_deck
        
    except DeckNotFoundError:
        logger.warning(f"Deck {deck_id} not found for update by user {current_user.id}")
        raise HTTPException(
            status_code=404,
            detail=f"Deck with ID {deck_id} not found or not authorized"
        )
        
    except (DeckValidationError, SerializationError) as e:
        logger.warning(f"Validation error updating deck {deck_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid deck data: {str(e)}"
        )
        
    except DatabaseError as e:
        logger.error(f"Database error updating deck {deck_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update deck due to database error"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error updating deck {deck_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while updating the deck"
        )


@router.delete("/decks/{deck_id}", status_code=204)
async def delete_single_user_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    deck_service: DeckService = Depends(get_deck_service)
):
    """
    Delete a deck for the authenticated user.
    
    Args:
        deck_id: ID of the deck to delete
        current_user: Authenticated user (injected)
        deck_service: Deck service instance (injected)
        
    Returns:
        None: 204 No Content on successful deletion
        
    Raises:
        HTTPException:
            - 404 Not Found: Deck not found or doesn't belong to user
            - 500 Internal Server Error: Database or unexpected errors
    """
    try:
        logger.info(f"Deleting deck {deck_id} for user {current_user.id}")
        success = await deck_service.delete_deck(deck_id, current_user)
        
        if not success:
            logger.warning(f"Deck {deck_id} not found for deletion by user {current_user.id}")
            raise HTTPException(
                status_code=404,
                detail=f"Deck with ID {deck_id} not found or not authorized"
            )
            
        logger.info(f"Successfully deleted deck {deck_id} for user {current_user.id}")
        return  # 204 No Content
        
    except DeckNotFoundError:
        logger.warning(f"Deck {deck_id} not found for deletion by user {current_user.id}")
        raise HTTPException(
            status_code=404,
            detail=f"Deck with ID {deck_id} not found or not authorized"
        )
        
    except DatabaseError as e:
        logger.error(f"Database error deleting deck {deck_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete deck due to database error"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error deleting deck {deck_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deleting the deck"
        )
