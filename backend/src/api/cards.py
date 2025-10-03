# backend/src/api/cards.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging

from ..models.card import Card
from ..services.clash_api_service import ClashRoyaleAPIService
from ..utils.dependencies import get_clash_api_service
from ..exceptions import ClashAPIError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cards", response_model=List[Card])
async def get_all_cards(
    clash_api: ClashRoyaleAPIService = Depends(get_clash_api_service),
):
    """
    Fetch all Clash Royale cards from the external API.

    Returns:
        List[Card]: List of all available cards with their properties

    Raises:
        HTTPException:
            - 503 Service Unavailable: When Clash Royale API is unavailable
            - 401 Unauthorized: When API key is invalid
            - 429 Too Many Requests: When API rate limit is exceeded
            - 500 Internal Server Error: For other unexpected errors
    """
    try:
        logger.info("Fetching cards from Clash Royale API")
        cards = await clash_api.get_cards()
        logger.info(f"Successfully retrieved {len(cards)} cards")
        return cards

    except ClashAPIError as e:
        logger.error(f"Clash API error: {e.message}")

        # Map ClashAPIError status codes to appropriate HTTP responses
        if e.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid Clash Royale API key")
        elif e.status_code == 403:
            raise HTTPException(
                status_code=403, detail="Access forbidden to Clash Royale API"
            )
        elif e.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Clash Royale API rate limit exceeded. Please try again later.",
            )
        elif e.status_code and e.status_code >= 500:
            raise HTTPException(
                status_code=503,
                detail="Clash Royale API is currently unavailable. Please try again later.",
            )
        else:
            # For network errors, timeouts, and other API issues
            raise HTTPException(
                status_code=503,
                detail="Unable to connect to Clash Royale API. Please try again later.",
            )

    except Exception as e:
        logger.error(f"Unexpected error fetching cards: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred while fetching cards"
        )
