# backend/tests/unit/test_services.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.src.services.clash_api_service import ClashRoyaleAPIService
from backend.src.services.deck_service import DeckService
from backend.src.models.deck import Deck
from backend.src.models.user import User
from backend.src.models.card import Card

@pytest.fixture
def mock_clash_api_service():
    service = ClashRoyaleAPIService(api_key="test_key")
    service.get_cards = AsyncMock(return_value=[])
    return service

@pytest.fixture
def mock_deck_service():
    service = DeckService()
    service._get_db_connection = MagicMock()
    return service

@pytest.mark.asyncio
async def test_clash_api_get_cards(mock_clash_api_service):
    cards = await mock_clash_api_service.get_cards()
    mock_clash_api_service.get_cards.assert_called_once()
    assert isinstance(cards, list)

@pytest.mark.asyncio
async def test_deck_service_create_deck(mock_deck_service):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_deck_service._get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 1

    user = User(id=1)
    card = Card(id=1, name="Archer", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/archer.png")
    deck_data = Deck(name="New Deck", cards=[card], evolution_slots=[], average_elixir=3.0)

    created_deck = await mock_deck_service.create_deck(deck_data, user)
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert created_deck.id == 1
