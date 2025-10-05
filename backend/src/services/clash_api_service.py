# backend/src/services/clash_api_service.py

import httpx
import logging
from typing import List, Optional
from ..models.card import Card

logger = logging.getLogger(__name__)


class ClashAPIError(Exception):
    """Raised when Clash Royale API calls fail"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ClashRoyaleAPIService:
    """Service for interacting with the Clash Royale API"""

    def __init__(self, api_key: str, base_url: str = "https://api.clashroyale.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.timeout = 30.0  # 30 second timeout

    async def get_cards(self) -> List[Card]:
        """
        Fetch all cards from the Clash Royale API and transform them to Card models.

        Returns:
            List[Card]: List of Card objects

        Raises:
            ClashAPIError: When API call fails or data transformation fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("Fetching cards from Clash Royale API...")

                response = await client.get(f"{self.base_url}/cards", headers=self.headers)

                # Handle HTTP errors
                if response.status_code == 401:
                    raise ClashAPIError("Invalid API key", status_code=401)
                elif response.status_code == 403:
                    raise ClashAPIError("API access forbidden", status_code=403)
                elif response.status_code == 429:
                    raise ClashAPIError("API rate limit exceeded", status_code=429)
                elif response.status_code >= 500:
                    raise ClashAPIError("Clash Royale API server error", status_code=response.status_code)
                elif response.status_code != 200:
                    raise ClashAPIError(
                        f"API request failed with status {response.status_code}", status_code=response.status_code
                    )

                # Parse JSON response
                try:
                    data = response.json()
                except Exception as e:
                    raise ClashAPIError(f"Failed to parse API response: {str(e)}")

                # Extract items from response
                if "items" not in data:
                    raise ClashAPIError("Invalid API response format: missing 'items' field")

                cards_data = data["items"]
                logger.info(f"Retrieved {len(cards_data)} cards from API")

                # Transform API data to Card models
                cards = []
                for card_data in cards_data:
                    try:
                        card = self._transform_card_data(card_data)
                        cards.append(card)
                    except Exception as e:
                        logger.warning(
                            f"Failed to transform card data for {card_data.get('name', 'unknown')}: {str(e)}"
                        )
                        # Continue processing other cards instead of failing completely
                        continue

                logger.info(f"Successfully transformed {len(cards)} cards")
                return cards

        except httpx.TimeoutException:
            raise ClashAPIError("API request timed out")
        except httpx.NetworkError as e:
            raise ClashAPIError(f"Network error: {str(e)}")
        except ClashAPIError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching cards: {str(e)}")
            raise ClashAPIError(f"Unexpected error: {str(e)}")

    def _transform_card_data(self, card_data: dict) -> Card:
        """
        Transform raw API card data to Card model.

        Args:
            card_data: Raw card data from API

        Returns:
            Card: Transformed Card object

        Raises:
            ValueError: When required fields are missing or invalid
        """
        try:
            # Extract required fields with validation
            card_id = card_data.get("id")
            if not card_id:
                raise ValueError("Missing card ID")

            name = card_data.get("name", "").strip()
            if not name:
                raise ValueError("Missing or empty card name")

            elixir_cost = card_data.get("elixirCost")
            if elixir_cost is None:
                raise ValueError("Missing elixir cost")

            # Handle rarity mapping from API format to our format
            api_rarity = card_data.get("rarity", "").lower()
            rarity_mapping = {
                "common": "Common",
                "rare": "Rare",
                "epic": "Epic",
                "legendary": "Legendary",
                "champion": "Champion",
            }
            rarity = rarity_mapping.get(api_rarity)
            if not rarity:
                raise ValueError(f"Invalid or missing rarity: {api_rarity}")

            # Handle type mapping from API format to our format
            api_type = card_data.get("type", "").lower()
            type_mapping = {"troop": "Troop", "spell": "Spell", "building": "Building"}
            card_type = type_mapping.get(api_type)
            if not card_type:
                raise ValueError(f"Invalid or missing type: {api_type}")

            # Extract optional fields
            arena = card_data.get("arena", {}).get("name") if card_data.get("arena") else None

            # Handle image URLs
            icons = card_data.get("iconUrls", {})
            image_url = icons.get("medium") or icons.get("large") or icons.get("small")
            if not image_url:
                raise ValueError("Missing card image URL")

            # Evolution image URL (may not exist for all cards)
            image_url_evo = icons.get("evolutionMedium") or icons.get("evolutionLarge")

            return Card(
                id=card_id,
                name=name,
                elixir_cost=elixir_cost,
                rarity=rarity,
                type=card_type,
                arena=arena,
                image_url=image_url,
                image_url_evo=image_url_evo,
            )

        except Exception as e:
            raise ValueError(f"Failed to transform card data: {str(e)}")
