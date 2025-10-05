# backend/src/utils/dependencies.py

from typing import Generator
from fastapi import Depends
from mysql.connector.cursor import MySQLCursor

from .config import settings
from .database import get_db_session
from ..services.clash_api_service import ClashRoyaleAPIService
from ..services.deck_service import DeckService
from ..services.card_service import CardService


def get_database_session() -> Generator[MySQLCursor, None, None]:
    """FastAPI dependency for database session with automatic transaction management."""
    with get_db_session() as session:
        yield session


def get_clash_api_service() -> ClashRoyaleAPIService:
    """FastAPI dependency for Clash Royale API service."""
    return ClashRoyaleAPIService(api_key=settings.clash_royale_api_key, base_url=settings.clash_royale_api_base_url)


def get_deck_service(db_session: MySQLCursor = Depends(get_database_session)) -> DeckService:
    """FastAPI dependency for deck service with database session injection."""
    return DeckService(db_session)


def get_card_service(db_session: MySQLCursor = Depends(get_database_session)) -> CardService:
    """FastAPI dependency for card service with database session injection."""
    return CardService(db_session)


# Dependency aliases for easier imports
DatabaseDep = Depends(get_database_session)
ClashAPIDep = Depends(get_clash_api_service)
DeckServiceDep = Depends(get_deck_service)
CardServiceDep = Depends(get_card_service)
