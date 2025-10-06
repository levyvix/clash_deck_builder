# backend/src/services/card_service.py

import logging
from typing import List, Optional
from mysql.connector import Error as MySQLError
from mysql.connector.cursor import MySQLCursor

from ..models.card import Card
from ..exceptions import DatabaseError
from ..utils.cache import cards_cache

logger = logging.getLogger(__name__)


class CardService:
    """Service for managing card database operations."""

    def __init__(self, db_session: MySQLCursor):
        """Initialize card service with database session dependency injection."""
        self.db_session = db_session

    async def get_all_cards(self) -> List[Card]:
        """
        Retrieve all cards from the database with caching.

        Uses in-memory cache with 24-hour TTL since card data rarely changes.

        Returns:
            List[Card]: List of all cards in the database

        Raises:
            DatabaseError: If database query fails
        """
        # Check cache first
        cache_key = "all_cards"
        cached_cards = cards_cache.get(cache_key)
        if cached_cards is not None:
            logger.info(f"Returning {len(cached_cards)} cards from cache")
            return cached_cards

        # Cache miss - fetch from database
        try:
            self.db_session.execute(
                """SELECT id, name, elixir_cost, rarity, type, arena,
                          image_url, image_url_evo
                   FROM cards
                   ORDER BY id"""
            )
            rows = self.db_session.fetchall()

            cards = []
            for row in rows:
                try:
                    card = self._transform_db_row_to_card(row)
                    cards.append(card)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping card {row.get('id')} due to validation error: {e}")
                    continue

            logger.info(f"Retrieved {len(cards)} cards from database and cached")

            # Store in cache
            cards_cache.set(cache_key, cards)

            return cards

        except MySQLError as e:
            logger.error(f"Database error retrieving cards: {e}")
            raise DatabaseError(f"Failed to retrieve cards from database: {e}", e)
        except Exception as e:
            logger.error(f"Unexpected error retrieving cards: {e}")
            raise DatabaseError(f"Unexpected error retrieving cards: {e}", e)

    async def get_card_by_id(self, card_id: int) -> Optional[Card]:
        """
        Retrieve a single card by ID with caching.

        Args:
            card_id: The unique identifier of the card

        Returns:
            Optional[Card]: The card if found, None otherwise

        Raises:
            DatabaseError: If database query fails
        """
        # Check cache first
        cache_key = f"card:{card_id}"
        cached_card = cards_cache.get(cache_key)
        if cached_card is not None:
            logger.debug(f"Returning card {card_id} from cache")
            return cached_card

        # Cache miss - fetch from database
        try:
            self.db_session.execute(
                """SELECT id, name, elixir_cost, rarity, type, arena,
                          image_url, image_url_evo
                   FROM cards
                   WHERE id = %s""",
                (card_id,),
            )
            row = self.db_session.fetchone()

            if not row:
                logger.debug(f"Card {card_id} not found in database")
                return None

            card = self._transform_db_row_to_card(row)
            logger.debug(f"Retrieved card {card_id} from database and cached")

            # Store in cache
            cards_cache.set(cache_key, card)

            return card

        except MySQLError as e:
            logger.error(f"Database error retrieving card {card_id}: {e}")
            raise DatabaseError(f"Failed to retrieve card {card_id}: {e}", e)
        except (ValueError, TypeError) as e:
            logger.error(f"Validation error for card {card_id}: {e}")
            raise DatabaseError(f"Invalid card data for card {card_id}: {e}", e)
        except Exception as e:
            logger.error(f"Unexpected error retrieving card {card_id}: {e}")
            raise DatabaseError(f"Unexpected error retrieving card {card_id}: {e}", e)

    def invalidate_cache(self) -> None:
        """Invalidate all card caches. Call this when card data is updated."""
        cards_cache.clear()
        logger.info("Card cache invalidated")

    def get_cache_stats(self) -> dict:
        """Get cache statistics for monitoring."""
        return cards_cache.get_stats()

    def _transform_db_row_to_card(self, row: dict) -> Card:
        """
        Transform a database row into a Card model instance.

        Args:
            row: Dictionary containing database row data

        Returns:
            Card: Card model instance

        Raises:
            ValueError: If card data validation fails
            TypeError: If required fields are missing
        """
        try:
            # Handle NULL values for optional fields
            arena = row.get("arena") if row.get("arena") is not None else None
            image_url_evo = row.get("image_url_evo") if row.get("image_url_evo") is not None else None

            # Create Card instance with validation
            card = Card(
                id=row["id"],
                name=row["name"],
                elixir_cost=row["elixir_cost"],
                rarity=row["rarity"],
                type=row["type"],
                arena=arena,
                image_url=row["image_url"],
                image_url_evo=image_url_evo,
            )

            return card

        except KeyError as e:
            logger.error(f"Missing required field in database row: {e}")
            raise TypeError(f"Missing required field: {e}")
        except ValueError as e:
            logger.error(f"Card validation failed: {e}")
            raise ValueError(f"Card validation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error transforming database row to card: {e}")
            raise TypeError(f"Failed to transform database row: {e}")
