"""
Integration tests for Cards API endpoint with database backend
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.api.cards import router as cards_router
from src.models.card import Card
from src.services.card_service import CardService
from src.exceptions import DatabaseError
from src.scripts.ingest_cards import ingest_cards


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    app = FastAPI()
    app.include_router(cards_router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


class TestCardsAPIWithDatabase:
    """Integration tests for GET /cards endpoint with database"""
    
    def test_get_cards_returns_database_data(self, app, client, clean_database):
        """Test GET /cards endpoint returns data from database"""
        # Insert test cards into database
        test_cards = [
            {
                'id': 26000100,
                'name': 'Knight',
                'elixir_cost': 3,
                'rarity': 'Common',
                'type': 'Troop',
                'arena': 'Training Camp',
                'image_url': 'https://example.com/knight.png',
                'image_url_evo': None
            },
            {
                'id': 27000100,
                'name': 'Cannon',
                'elixir_cost': 3,
                'rarity': 'Common',
                'type': 'Building',
                'arena': 'Training Camp',
                'image_url': 'https://example.com/cannon.png',
                'image_url_evo': None
            },
            {
                'id': 28000100,
                'name': 'Fireball',
                'elixir_cost': 4,
                'rarity': 'Rare',
                'type': 'Spell',
                'arena': 'Spell Valley',
                'image_url': 'https://example.com/fireball.png',
                'image_url_evo': 'https://example.com/fireball_evo.png'
            }
        ]
        
        inserted, updated, errors = ingest_cards(test_cards)
        assert inserted == 3
        assert errors == 0
        
        # Mock the card service to use test database
        def mock_get_card_service():
            cursor = clean_database.connection.cursor(dictionary=True)
            return CardService(cursor)
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        # Make API request
        response = client.get("/cards")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure and data
        assert len(data) == 3
        assert isinstance(data, list)
        
        # Verify first card
        assert data[0]['id'] == 26000100
        assert data[0]['name'] == 'Knight'
        assert data[0]['elixir_cost'] == 3
        assert data[0]['rarity'] == 'Common'
        assert data[0]['type'] == 'Troop'
        assert data[0]['arena'] == 'Training Camp'
        assert data[0]['image_url'] == 'https://example.com/knight.png'
        assert data[0]['image_url_evo'] is None
        
        # Verify card with evolution
        fireball = next(c for c in data if c['id'] == 28000100)
        assert fireball['image_url_evo'] == 'https://example.com/fireball_evo.png'
        
        app.dependency_overrides.clear()
    
    def test_get_cards_with_empty_database(self, app, client, clean_database):
        """Test GET /cards endpoint with empty database returns empty array"""
        # Don't insert any cards - database is clean
        
        def mock_get_card_service():
            cursor = clean_database.connection.cursor(dictionary=True)
            return CardService(cursor)
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
        assert isinstance(data, list)
        
        app.dependency_overrides.clear()
    
    def test_get_cards_response_format_matches_card_model(self, app, client, clean_database):
        """Test that endpoint response format matches Card model structure"""
        # Insert a card with all fields populated
        test_card = {
            'id': 26000110,
            'name': 'Test Card',
            'elixir_cost': 5,
            'rarity': 'Epic',
            'type': 'Troop',
            'arena': 'Arena 10',
            'image_url': 'https://example.com/test.png',
            'image_url_evo': 'https://example.com/test_evo.png'
        }
        
        inserted, updated, errors = ingest_cards([test_card])
        assert inserted == 1
        
        def mock_get_card_service():
            cursor = clean_database.connection.cursor(dictionary=True)
            return CardService(cursor)
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        card = data[0]
        
        # Verify all Card model fields are present
        required_fields = ['id', 'name', 'elixir_cost', 'rarity', 'type', 'arena', 'image_url', 'image_url_evo']
        for field in required_fields:
            assert field in card, f"Missing field: {field}"
        
        # Verify field types
        assert isinstance(card['id'], int)
        assert isinstance(card['name'], str)
        assert isinstance(card['elixir_cost'], int)
        assert isinstance(card['rarity'], str)
        assert isinstance(card['type'], str)
        assert isinstance(card['arena'], str) or card['arena'] is None
        assert isinstance(card['image_url'], str)
        assert isinstance(card['image_url_evo'], str) or card['image_url_evo'] is None
        
        # Verify values match Card model validation
        assert card['id'] > 0
        assert len(card['name']) > 0
        assert 0 <= card['elixir_cost'] <= 10
        assert card['rarity'] in ['Common', 'Rare', 'Epic', 'Legendary', 'Champion']
        assert card['type'] in ['Troop', 'Spell', 'Building']
        
        app.dependency_overrides.clear()
    
    def test_get_cards_with_null_optional_fields(self, app, client, clean_database):
        """Test endpoint correctly handles NULL optional fields"""
        # Insert card with NULL optional fields
        test_card = {
            'id': 26000120,
            'name': 'Minimal Card',
            'elixir_cost': 2,
            'rarity': 'Common',
            'type': 'Troop',
            'arena': None,  # NULL
            'image_url': 'https://example.com/minimal.png',
            'image_url_evo': None  # NULL
        }
        
        inserted, updated, errors = ingest_cards([test_card])
        assert inserted == 1
        
        def mock_get_card_service():
            cursor = clean_database.connection.cursor(dictionary=True)
            return CardService(cursor)
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        card = data[0]
        assert card['arena'] is None
        assert card['image_url_evo'] is None
        
        app.dependency_overrides.clear()
    
    def test_get_cards_ordered_by_id(self, app, client, clean_database):
        """Test that cards are returned ordered by ID"""
        # Insert cards in non-sequential order
        test_cards = [
            {
                'id': 28000130,
                'name': 'Spell Card',
                'elixir_cost': 4,
                'rarity': 'Rare',
                'type': 'Spell',
                'arena': None,
                'image_url': 'https://example.com/spell.png',
                'image_url_evo': None
            },
            {
                'id': 26000130,
                'name': 'Troop Card',
                'elixir_cost': 3,
                'rarity': 'Common',
                'type': 'Troop',
                'arena': None,
                'image_url': 'https://example.com/troop.png',
                'image_url_evo': None
            },
            {
                'id': 27000130,
                'name': 'Building Card',
                'elixir_cost': 5,
                'rarity': 'Epic',
                'type': 'Building',
                'arena': None,
                'image_url': 'https://example.com/building.png',
                'image_url_evo': None
            }
        ]
        
        inserted, updated, errors = ingest_cards(test_cards)
        assert inserted == 3
        
        def mock_get_card_service():
            cursor = clean_database.connection.cursor(dictionary=True)
            return CardService(cursor)
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify cards are ordered by ID
        assert data[0]['id'] == 26000130
        assert data[1]['id'] == 27000130
        assert data[2]['id'] == 28000130
        
        app.dependency_overrides.clear()


class TestCardsAPIErrorHandling:
    """Test error handling for Cards API with database"""
    
    def test_get_cards_database_connection_error(self, app, client):
        """Test GET /cards with database connection failure returns 503"""
        from mysql.connector import Error as MySQLError
        
        # Create a MySQL connection error with appropriate error code
        mysql_error = MySQLError()
        mysql_error.errno = 2003  # Can't connect to MySQL server
        
        # Mock card service to raise DatabaseError with MySQL connection error
        mock_service = AsyncMock()
        mock_service.get_all_cards.side_effect = DatabaseError(
            "Database connection failed", mysql_error
        )
        
        def mock_get_card_service():
            return mock_service
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 503
        assert "database" in response.json()['detail'].lower()
        
        app.dependency_overrides.clear()
    
    def test_get_cards_database_query_error(self, app, client):
        """Test GET /cards with database query error returns 500"""
        # Mock card service to raise DatabaseError without connection error code
        mock_service = AsyncMock()
        mock_service.get_all_cards.side_effect = DatabaseError(
            "Query execution failed", None
        )
        
        def mock_get_card_service():
            return mock_service
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        # Should return 500 for query errors (not connection errors)
        assert response.status_code == 500
        assert "database" in response.json()['detail'].lower()
        
        app.dependency_overrides.clear()
    
    def test_get_cards_unexpected_error(self, app, client):
        """Test GET /cards with unexpected error returns 500"""
        # Mock card service to raise unexpected exception
        mock_service = AsyncMock()
        mock_service.get_all_cards.side_effect = Exception("Unexpected error")
        
        def mock_get_card_service():
            return mock_service
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 500
        assert "unexpected error" in response.json()['detail'].lower()
        
        app.dependency_overrides.clear()


class TestBackwardCompatibility:
    """Test backward compatibility with existing Card model"""
    
    def test_response_format_unchanged_from_api_version(self, app, client, clean_database):
        """Test that response format is identical to previous API-based version"""
        # Insert a card that matches the old API response format
        test_card = {
            'id': 26000140,
            'name': 'Knight',
            'elixir_cost': 3,
            'rarity': 'Common',
            'type': 'Troop',
            'arena': 'Training Camp',
            'image_url': 'https://api-assets.clashroyale.com/cards/300/knight.png',
            'image_url_evo': None
        }
        
        inserted, updated, errors = ingest_cards([test_card])
        assert inserted == 1
        
        def mock_get_card_service():
            cursor = clean_database.connection.cursor(dictionary=True)
            return CardService(cursor)
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure matches Card model exactly
        card = data[0]
        
        # These are the exact fields from the Card model
        expected_fields = {
            'id', 'name', 'elixir_cost', 'rarity', 'type', 
            'arena', 'image_url', 'image_url_evo'
        }
        actual_fields = set(card.keys())
        
        assert actual_fields == expected_fields, \
            f"Field mismatch. Expected: {expected_fields}, Got: {actual_fields}"
        
        app.dependency_overrides.clear()
    
    def test_image_urls_remain_external(self, app, client, clean_database):
        """Test that image URLs remain as external CDN links"""
        test_card = {
            'id': 26000150,
            'name': 'Test Card',
            'elixir_cost': 4,
            'rarity': 'Rare',
            'type': 'Troop',
            'arena': None,
            'image_url': 'https://api-assets.clashroyale.com/cards/300/test.png',
            'image_url_evo': 'https://api-assets.clashroyale.com/cards/300/test_evo.png'
        }
        
        inserted, updated, errors = ingest_cards([test_card])
        assert inserted == 1
        
        def mock_get_card_service():
            cursor = clean_database.connection.cursor(dictionary=True)
            return CardService(cursor)
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 200
        data = response.json()
        card = data[0]
        
        # Verify URLs are external (start with https://)
        assert card['image_url'].startswith('https://')
        assert card['image_url_evo'].startswith('https://')
        
        # Verify they point to CDN
        assert 'clashroyale.com' in card['image_url']
        assert 'clashroyale.com' in card['image_url_evo']
        
        app.dependency_overrides.clear()
    
    def test_card_model_validation_still_applies(self, app, client, clean_database):
        """Test that Card model validation rules are still enforced"""
        # Try to insert a card with invalid rarity (should be caught by ingestion)
        # But if it somehow gets through, the API should handle it
        
        # Insert valid card
        test_card = {
            'id': 26000160,
            'name': 'Valid Card',
            'elixir_cost': 3,
            'rarity': 'Common',  # Valid rarity
            'type': 'Troop',
            'arena': None,
            'image_url': 'https://example.com/valid.png',
            'image_url_evo': None
        }
        
        inserted, updated, errors = ingest_cards([test_card])
        assert inserted == 1
        
        def mock_get_card_service():
            cursor = clean_database.connection.cursor(dictionary=True)
            return CardService(cursor)
        
        from src.utils.dependencies import get_card_service
        app.dependency_overrides[get_card_service] = mock_get_card_service
        
        response = client.get("/cards")
        
        assert response.status_code == 200
        data = response.json()
        card = data[0]
        
        # Verify Card model validation constraints
        assert card['rarity'] in ['Common', 'Rare', 'Epic', 'Legendary', 'Champion']
        assert card['type'] in ['Troop', 'Spell', 'Building']
        assert 0 <= card['elixir_cost'] <= 10
        assert card['id'] > 0
        assert len(card['name']) > 0
        
        app.dependency_overrides.clear()
