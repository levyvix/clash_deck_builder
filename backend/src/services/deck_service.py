# backend/src/services/deck_service.py

import mysql.connector
from typing import List, Optional
from ..models.deck import Deck
from ..models.user import User
from ..models.card import Card
from ..utils.config import DATABASE_URL

class DeckService:
    def __init__(self):
        # Parse DATABASE_URL to get connection details
        # For simplicity, assuming direct connection details for now
        self.db_config = {
            "host": "localhost",
            "user": "user",
            "password": "password",
            "database": "database_name"
        }

    def _get_db_connection(self):
        return mysql.connector.connect(**self.db_config)

    async def create_deck(self, deck: Deck, user: User) -> Deck:
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert deck data
            cursor.execute(
                "INSERT INTO decks (name, user_id, cards, evolution_slots, average_elixir) VALUES (%s, %s, %s, %s, %s)",
                (deck.name, user.id, deck.cards.json(), deck.evolution_slots.json(), deck.average_elixir)
            )
            deck.id = cursor.lastrowid
            conn.commit()
            return deck
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    async def get_deck(self, deck_id: int, user: User) -> Optional[Deck]:
        conn = self._get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, name, user_id, cards, evolution_slots, average_elixir FROM decks WHERE id = %s AND user_id = %s",
                (deck_id, user.id)
            )
            row = cursor.fetchone()
            if row:
                # Deserialize JSON fields back to List[Card]
                row["cards"] = [Card.parse_raw(card_json) for card_json in row["cards"]]
                row["evolution_slots"] = [Card.parse_raw(card_json) for card_json in row["evolution_slots"]]
                return Deck(**row)
            return None
        finally:
            cursor.close()
            conn.close()

    async def get_user_decks(self, user: User) -> List[Deck]:
        conn = self._get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, name, user_id, cards, evolution_slots, average_elixir FROM decks WHERE user_id = %s",
                (user.id,)
            )
            decks = []
            for row in cursor.fetchall():
                row["cards"] = [Card.parse_raw(card_json) for card_json in row["cards"]]
                row["evolution_slots"] = [Card.parse_raw(card_json) for card_json in row["evolution_slots"]]
                decks.append(Deck(**row))
            return decks
        finally:
            cursor.close()
            conn.close()

    async def update_deck(self, deck: Deck, user: User) -> Optional[Deck]:
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE decks SET name = %s, cards = %s, evolution_slots = %s, average_elixir = %s WHERE id = %s AND user_id = %s",
                (deck.name, deck.cards.json(), deck.evolution_slots.json(), deck.average_elixir, deck.id, user.id)
            )
            conn.commit()
            return deck
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    async def delete_deck(self, deck_id: int, user: User) -> bool:
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM decks WHERE id = %s AND user_id = %s",
                (deck_id, user.id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()