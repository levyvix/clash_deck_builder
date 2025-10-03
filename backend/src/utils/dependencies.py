# backend/src/utils/dependencies.py

from typing import Generator
from fastapi import Depends
from mysql.connector.cursor import MySQLCursor

from .config import settings
from .database import get_db_session
from ..services.clash_api_service import ClashAPIService


def get_database_session() -> Generator[MySQLCursor, None, None]:
    """FastAPI dependency for database session with automatic transaction management."""
    with get_db_session() as session:
        yield session


def get_clash_api_service() -> ClashAPIService:
    """FastAPI dependency for Clash Royale API service."""
    return ClashAPIService(
        api_key=settings.clash_royale_api_key,
        base_url=settings.clash_royale_api_base_url
    )


# Dependency aliases for easier imports
DatabaseDep = Depends(get_database_session)
ClashAPIDep = Depends(get_clash_api_service)