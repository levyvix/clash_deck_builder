# backend/src/services/deck_service.py

import json
import logging
from typing import List, Optional
from mysql.connector import Error as MySQLError
from mysql.connector.cursor import MySQLCursor

from ..models.deck import Deck
from ..models.user import User
from ..models.card import Card
from ..exceptions import DatabaseError, DeckNotFoundError, SerializationError, DeckLimitExceededError

logger = logging.getLogger(__name__)


class DeckService:
    """Service for managing deck CRUD operations with proper database integration."""

    def __init__(self, db_session: MySQLCursor):
        """Initialize deck service with database session dependency injection."""
        self.db_session = db_session
        self.max_decks_per_user = 20

    def _serialize_cards(self, cards: List[Card]) -> str:
        """Serialize list of cards to JSON string."""
        try:
            return json.dumps([card.model_dump() for card in cards])
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize cards: {e}")
            raise SerializationError(f"Failed to serialize cards: {e}", "cards")

    def _deserialize_cards(self, cards_json: str) -> List[Card]:
        """Deserialize JSON string to list of cards."""
        try:
            if not cards_json:
                return []
            cards_data = json.loads(cards_json)
            return [Card(**card_data) for card_data in cards_data]
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.error(f"Failed to deserialize cards: {e}")
            raise SerializationError(f"Failed to deserialize cards: {e}", "cards")

    async def _check_deck_limit(self, user_id: str) -> None:
        """Check if user has reached the maximum deck limit."""
        try:
            self.db_session.execute("SELECT COUNT(*) as deck_count FROM decks WHERE user_id = %s", (user_id,))
            result = self.db_session.fetchone()
            deck_count = result["deck_count"] if result else 0

            if deck_count >= self.max_decks_per_user:
                raise DeckLimitExceededError(user_id, self.max_decks_per_user)

        except MySQLError as e:
            logger.error(f"Database error checking deck limit for user {user_id}: {e}")
            raise DatabaseError(f"Failed to check deck limit: {e}", e)

    async def create_deck(self, deck: Deck, user: User) -> Deck:
        """Create a new deck for the user with proper transaction handling."""
        try:
            # Check deck limit before creating
            await self._check_deck_limit(user.id)

            # Ensure average elixir is calculated
            if deck.average_elixir is None:
                deck.update_average_elixir()

            # Serialize card data
            cards_json = self._serialize_cards(deck.cards)
            evolution_slots_json = self._serialize_cards(deck.evolution_slots)

            # Insert deck data
            self.db_session.execute(
                """INSERT INTO decks (name, user_id, cards, evolution_slots, average_elixir) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (deck.name, user.id, cards_json, evolution_slots_json, deck.average_elixir),
            )

            # Get the inserted deck ID
            deck.id = self.db_session.lastrowid
            deck.user_id = user.id

            logger.info(f"Created deck {deck.id} for user {user.id}")
            return deck

        except MySQLError as e:
            logger.error(f"Database error creating deck for user {user.id}: {e}")
            raise DatabaseError(f"Failed to create deck: {e}", e)
        except (SerializationError, DeckLimitExceededError):
            # Re-raise custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating deck for user {user.id}: {e}")
            raise DatabaseError(f"Unexpected error creating deck: {e}", e)

    async def get_deck(self, deck_id: int, user: User) -> Optional[Deck]:
        """Get a specific deck by ID for the user."""
        try:
            self.db_session.execute(
                """SELECT id, name, user_id, cards, evolution_slots, average_elixir 
                   FROM decks WHERE id = %s AND user_id = %s""",
                (deck_id, user.id),
            )
            row = self.db_session.fetchone()

            if not row:
                return None

            # Deserialize JSON fields back to List[Card]
            cards = self._deserialize_cards(row["cards"])
            evolution_slots = self._deserialize_cards(row["evolution_slots"])

            deck = Deck(
                id=row["id"],
                name=row["name"],
                user_id=row["user_id"],
                cards=cards,
                evolution_slots=evolution_slots,
                average_elixir=row["average_elixir"],
            )

            logger.debug(f"Retrieved deck {deck_id} for user {user.id}")
            return deck

        except MySQLError as e:
            logger.error(f"Database error retrieving deck {deck_id} for user {user.id}: {e}")
            raise DatabaseError(f"Failed to retrieve deck: {e}", e)
        except SerializationError:
            # Re-raise serialization errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving deck {deck_id} for user {user.id}: {e}")
            raise DatabaseError(f"Unexpected error retrieving deck: {e}", e)

    async def get_user_decks(self, user: User) -> List[Deck]:
        """Get all decks for a specific user."""
        try:
            self.db_session.execute(
                """SELECT id, name, user_id, cards, evolution_slots, average_elixir 
                   FROM decks WHERE user_id = %s ORDER BY id DESC""",
                (user.id,),
            )
            rows = self.db_session.fetchall()

            decks = []
            for row in rows:
                try:
                    # Deserialize JSON fields back to List[Card]
                    cards = self._deserialize_cards(row["cards"])
                    evolution_slots = self._deserialize_cards(row["evolution_slots"])

                    deck = Deck(
                        id=row["id"],
                        name=row["name"],
                        user_id=row["user_id"],
                        cards=cards,
                        evolution_slots=evolution_slots,
                        average_elixir=row["average_elixir"],
                    )
                    decks.append(deck)

                except SerializationError as e:
                    logger.warning(f"Skipping deck {row['id']} due to serialization error: {e}")
                    continue

            logger.debug(f"Retrieved {len(decks)} decks for user {user.id}")
            return decks

        except MySQLError as e:
            logger.error(f"Database error retrieving decks for user {user.id}: {e}")
            raise DatabaseError(f"Failed to retrieve user decks: {e}", e)
        except Exception as e:
            logger.error(f"Unexpected error retrieving decks for user {user.id}: {e}")
            raise DatabaseError(f"Unexpected error retrieving user decks: {e}", e)

    async def update_deck(self, deck: Deck, user: User) -> Optional[Deck]:
        """Update an existing deck with proper transaction handling."""
        try:
            # Ensure the deck exists and belongs to the user
            existing_deck = await self.get_deck(deck.id, user)
            if not existing_deck:
                raise DeckNotFoundError(deck.id, user.id)

            # Ensure average elixir is calculated
            if deck.average_elixir is None:
                deck.update_average_elixir()

            # Serialize card data
            cards_json = self._serialize_cards(deck.cards)
            evolution_slots_json = self._serialize_cards(deck.evolution_slots)

            # Update deck data
            self.db_session.execute(
                """UPDATE decks SET name = %s, cards = %s, evolution_slots = %s, average_elixir = %s 
                   WHERE id = %s AND user_id = %s""",
                (deck.name, cards_json, evolution_slots_json, deck.average_elixir, deck.id, user.id),
            )

            # Check if any rows were affected
            if self.db_session.rowcount == 0:
                raise DeckNotFoundError(deck.id, user.id)

            logger.info(f"Updated deck {deck.id} for user {user.id}")
            return deck

        except MySQLError as e:
            logger.error(f"Database error updating deck {deck.id} for user {user.id}: {e}")
            raise DatabaseError(f"Failed to update deck: {e}", e)
        except (SerializationError, DeckNotFoundError):
            # Re-raise custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating deck {deck.id} for user {user.id}: {e}")
            raise DatabaseError(f"Unexpected error updating deck: {e}", e)

    async def delete_deck(self, deck_id: int, user: User) -> bool:
        """Delete a deck with proper transaction handling."""
        try:
            # Check if deck exists and belongs to user
            existing_deck = await self.get_deck(deck_id, user)
            if not existing_deck:
                raise DeckNotFoundError(deck_id, user.id)

            # Delete the deck
            self.db_session.execute("DELETE FROM decks WHERE id = %s AND user_id = %s", (deck_id, user.id))

            # Check if any rows were affected
            deleted = self.db_session.rowcount > 0

            if deleted:
                logger.info(f"Deleted deck {deck_id} for user {user.id}")
            else:
                logger.warning(f"No deck deleted for ID {deck_id} and user {user.id}")

            return deleted

        except MySQLError as e:
            logger.error(f"Database error deleting deck {deck_id} for user {user.id}: {e}")
            raise DatabaseError(f"Failed to delete deck: {e}", e)
        except DeckNotFoundError:
            # Re-raise deck not found errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting deck {deck_id} for user {user.id}: {e}")
            raise DatabaseError(f"Unexpected error deleting deck: {e}", e)

    async def get_deck_count(self, user: User) -> int:
        """Get the total number of decks for a user."""
        try:
            self.db_session.execute("SELECT COUNT(*) as deck_count FROM decks WHERE user_id = %s", (user.id,))
            result = self.db_session.fetchone()
            count = result["deck_count"] if result else 0

            logger.debug(f"User {user.id} has {count} decks")
            return count

        except MySQLError as e:
            logger.error(f"Database error getting deck count for user {user.id}: {e}")
            raise DatabaseError(f"Failed to get deck count: {e}", e)
        except Exception as e:
            logger.error(f"Unexpected error getting deck count for user {user.id}: {e}")
            raise DatabaseError(f"Unexpected error getting deck count: {e}", e)
