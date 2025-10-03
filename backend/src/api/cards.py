# backend/src/api/cards.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging
from mysql.connector import Error as MySQLError

from ..models.card import Card
from ..services.card_service import CardService
from ..utils.dependencies import get_card_service
from ..exceptions import DatabaseError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cards", response_model=List[Card])
async def get_all_cards(
    card_service: CardService = Depends(get_card_service),
):
    """
    Fetch all Clash Royale cards from the database.

    Returns:
        List[Card]: List of all available cards with their properties

    Raises:
        HTTPException:
            - 503 Service Unavailable: When database connection fails
            - 500 Internal Server Error: For database query errors or unexpected errors
    """
    try:
        logger.info("Fetching cards from database")
        cards = await card_service.get_all_cards()
        logger.info(f"Successfully retrieved {len(cards)} cards from database")
        return cards

    except DatabaseError as e:
        logger.error(f"Database error: {e.message}")

        # Check if it's a connection error by examining the original error
        if e.original_error and isinstance(e.original_error, MySQLError):
            # Connection-related MySQL error codes
            connection_error_codes = [2003, 2006, 2013, 2055]  # Can't connect, server gone away, lost connection, etc.
            if hasattr(e.original_error, 'errno') and e.original_error.errno in connection_error_codes:
                raise HTTPException(
                    status_code=503,
                    detail="Database temporarily unavailable. Please try again later."
                )
        
        # For all other database errors (query failures, data integrity issues, etc.)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve cards from database"
        )

    except Exception as e:
        logger.error(f"Unexpected error fetching cards: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred while fetching cards"
        )
