"""
Integration tests for card database operations and ingestion workflow
"""
import pytest
import json
import tempfile
from pathlib import Path
from typing import List

from src.scripts.ingest_cards import (
    load_json_file,
    determine_card_type,
    transform_card_data,
    ingest_cards
)
from src.services.card_service import CardService
from src.models.card import Card
from src.exceptions import DatabaseError


class TestCardIngestionWorkflow:
    """Test full ingestion workflow with test JSON data"""
    
    def test_full_ingestion_workflow_with_test_data(self, clean_database):
        """Test complete ingestion workflow from JSON to database"""
        # Create test JSON data
        test_cards_data = {
            "items": [
                {
                    "id": 26000000,
                    "name": "Knight",
                    "elixirCost": 3,
                    "rarity": "common",
                    "iconUrls": {
                        "medium": "https://example.com/knight.png"
                    },
                    "arena": {"name": "Training Camp"}
                },
                {
                    "id": 27000000,
                    "name": "Cannon",
                    "elixirCost": 3,
                    "rarity": "common",
                    "iconUrls": {
                        "medium": "https://example.com/cannon.png"
                    }
                },
                {
                    "id": 28000000,
                    "name": "Fireball",
                    "elixirCost": 4,
                    "rarity": "rare",
                    "iconUrls": {
                        "medium": "https://example.com/fireball.png",
                        "evolutionMedium": "https://example.com/fireball_evo.png"
                    },
                    "arena": {"name": "Spell Valley"}
                }
            ]
        }
        
        # Write test data to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_cards_data, f)
            temp_file_path = f.name
        
        try:
            # Step 1: Load JSON file
            data = load_json_file(temp_file_path)
            assert data is not None
            assert len(data['items']) == 3
            
            # Step 2: Transform card data
            transformed_cards = []
            for card_json in data['items']:
                transformed = transform_card_data(card_json)
                assert transformed is not None
                transformed_cards.append(transformed)
            
            assert len(transformed_cards) == 3
            
            # Verify transformations
            assert transformed_cards[0]['type'] == 'Troop'
            assert transformed_cards[0]['rarity'] == 'Common'
            assert transformed_cards[0]['arena'] == 'Training Camp'
            
            assert transformed_cards[1]['type'] == 'Building'
            assert transformed_cards[1]['arena'] is None
            
            assert transformed_cards[2]['type'] == 'Spell'
            assert transformed_cards[2]['image_url_evo'] == 'https://example.com/fireball_evo.png'
            
            # Step 3: Ingest cards into database
            inserted, updated, errors = ingest_cards(transformed_cards)
            
            assert inserted == 3
            assert updated == 0
            assert errors == 0
            
            # Step 4: Verify cards are in database
            count = clean_database.get_table_count('cards')
            assert count == 3
            
            # Verify specific card data
            cards_in_db = clean_database.execute_query(
                "SELECT * FROM cards WHERE id = %s", (26000000,)
            )
            assert len(cards_in_db) == 1
            assert cards_in_db[0]['name'] == 'Knight'
            assert cards_in_db[0]['elixir_cost'] == 3
            assert cards_in_db[0]['type'] == 'Troop'
            
        finally:
            # Clean up temp file
            Path(temp_file_path).unlink()
    
    def test_ingestion_with_missing_optional_fields(self, clean_database):
        """Test ingestion with cards missing optional fields"""
        test_cards_data = {
            "items": [
                {
                    "id": 26000001,
                    "name": "Archers",
                    "elixirCost": 3,
                    "rarity": "common",
                    "iconUrls": {
                        "medium": "https://example.com/archers.png"
                    }
                    # No arena, no evolutionMedium
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_cards_data, f)
            temp_file_path = f.name
        
        try:
            data = load_json_file(temp_file_path)
            transformed_cards = []
            for card_json in data['items']:
                transformed = transform_card_data(card_json)
                transformed_cards.append(transformed)
            
            # Verify optional fields are None
            assert transformed_cards[0]['arena'] is None
            assert transformed_cards[0]['image_url_evo'] is None
            
            inserted, updated, errors = ingest_cards(transformed_cards)
            assert inserted == 1
            assert errors == 0
            
            # Verify in database
            cards_in_db = clean_database.execute_query(
                "SELECT * FROM cards WHERE id = %s", (26000001,)
            )
            assert cards_in_db[0]['arena'] is None
            assert cards_in_db[0]['image_url_evo'] is None
            
        finally:
            Path(temp_file_path).unlink()
    
    def test_ingestion_with_invalid_card_skipped(self, clean_database):
        """Test that invalid cards are skipped during ingestion"""
        test_cards_data = {
            "items": [
                {
                    "id": 26000002,
                    "name": "Valid Card",
                    "elixirCost": 3,
                    "rarity": "common",
                    "iconUrls": {
                        "medium": "https://example.com/valid.png"
                    }
                },
                {
                    # Missing required fields
                    "id": 26000003,
                    "name": "Invalid Card"
                    # Missing elixirCost, rarity, iconUrls
                },
                {
                    "id": 26000004,
                    "name": "Another Valid Card",
                    "elixirCost": 4,
                    "rarity": "rare",
                    "iconUrls": {
                        "medium": "https://example.com/valid2.png"
                    }
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_cards_data, f)
            temp_file_path = f.name
        
        try:
            data = load_json_file(temp_file_path)
            transformed_cards = []
            for card_json in data['items']:
                transformed = transform_card_data(card_json)
                if transformed:  # Only add valid cards
                    transformed_cards.append(transformed)
            
            # Should have 2 valid cards
            assert len(transformed_cards) == 2
            
            inserted, updated, errors = ingest_cards(transformed_cards)
            assert inserted == 2
            
            # Verify only valid cards are in database
            count = clean_database.get_table_count('cards')
            assert count == 2
            
        finally:
            Path(temp_file_path).unlink()


class TestCardRetrieval:
    """Test card retrieval after ingestion"""
    
    def test_retrieve_cards_after_ingestion(self, clean_database):
        """Test retrieving cards using CardService after ingestion"""
        # Insert test cards directly
        test_cards = [
            {
                'id': 26000010,
                'name': 'Test Knight',
                'elixir_cost': 3,
                'rarity': 'Common',
                'type': 'Troop',
                'arena': 'Arena 1',
                'image_url': 'https://example.com/knight.png',
                'image_url_evo': None
            },
            {
                'id': 28000010,
                'name': 'Test Fireball',
                'elixir_cost': 4,
                'rarity': 'Rare',
                'type': 'Spell',
                'arena': 'Arena 2',
                'image_url': 'https://example.com/fireball.png',
                'image_url_evo': 'https://example.com/fireball_evo.png'
            }
        ]
        
        inserted, updated, errors = ingest_cards(test_cards)
        assert inserted == 2
        assert errors == 0
        
        # Retrieve cards using CardService
        cursor = clean_database.connection.cursor(dictionary=True)
        card_service = CardService(cursor)
        
        # Use asyncio to run async method
        import asyncio
        cards = asyncio.run(card_service.get_all_cards())
        
        assert len(cards) == 2
        assert isinstance(cards[0], Card)
        assert cards[0].name == 'Test Knight'
        assert cards[0].elixir_cost == 3
        assert cards[0].type == 'Troop'
        
        assert cards[1].name == 'Test Fireball'
        assert cards[1].image_url_evo == 'https://example.com/fireball_evo.png'
        
        cursor.close()
    
    def test_retrieve_single_card_by_id(self, clean_database):
        """Test retrieving a single card by ID"""
        test_card = {
            'id': 26000020,
            'name': 'Test Giant',
            'elixir_cost': 5,
            'rarity': 'Rare',
            'type': 'Troop',
            'arena': 'Arena 3',
            'image_url': 'https://example.com/giant.png',
            'image_url_evo': None
        }
        
        inserted, updated, errors = ingest_cards([test_card])
        assert inserted == 1
        
        # Retrieve specific card
        cursor = clean_database.connection.cursor(dictionary=True)
        card_service = CardService(cursor)
        
        import asyncio
        card = asyncio.run(card_service.get_card_by_id(26000020))
        
        assert card is not None
        assert card.id == 26000020
        assert card.name == 'Test Giant'
        assert card.elixir_cost == 5
        
        cursor.close()
    
    def test_retrieve_nonexistent_card_returns_none(self, clean_database):
        """Test retrieving a card that doesn't exist"""
        cursor = clean_database.connection.cursor(dictionary=True)
        card_service = CardService(cursor)
        
        import asyncio
        card = asyncio.run(card_service.get_card_by_id(99999999))
        
        assert card is None
        
        cursor.close()
    
    def test_retrieve_cards_with_null_optional_fields(self, clean_database):
        """Test retrieving cards with NULL optional fields"""
        test_card = {
            'id': 26000030,
            'name': 'Test Minions',
            'elixir_cost': 3,
            'rarity': 'Common',
            'type': 'Troop',
            'arena': None,  # NULL arena
            'image_url': 'https://example.com/minions.png',
            'image_url_evo': None  # NULL evolution image
        }
        
        inserted, updated, errors = ingest_cards([test_card])
        assert inserted == 1
        
        cursor = clean_database.connection.cursor(dictionary=True)
        card_service = CardService(cursor)
        
        import asyncio
        cards = asyncio.run(card_service.get_all_cards())
        
        assert len(cards) == 1
        assert cards[0].arena is None
        assert cards[0].image_url_evo is None
        
        cursor.close()


class TestUpsertBehavior:
    """Test upsert behavior (insert then update same card)"""
    
    def test_insert_then_update_same_card(self, clean_database):
        """Test that re-ingesting a card updates existing record"""
        # Initial insert
        initial_card = {
            'id': 26000040,
            'name': 'Initial Name',
            'elixir_cost': 3,
            'rarity': 'Common',
            'type': 'Troop',
            'arena': 'Arena 1',
            'image_url': 'https://example.com/initial.png',
            'image_url_evo': None
        }
        
        inserted, updated, errors = ingest_cards([initial_card])
        assert inserted == 1
        assert updated == 0
        
        # Verify initial data
        cards_in_db = clean_database.execute_query(
            "SELECT * FROM cards WHERE id = %s", (26000040,)
        )
        assert cards_in_db[0]['name'] == 'Initial Name'
        assert cards_in_db[0]['elixir_cost'] == 3
        
        # Update with new data
        updated_card = {
            'id': 26000040,  # Same ID
            'name': 'Updated Name',
            'elixir_cost': 4,  # Changed
            'rarity': 'Rare',  # Changed
            'type': 'Troop',
            'arena': 'Arena 2',  # Changed
            'image_url': 'https://example.com/updated.png',  # Changed
            'image_url_evo': 'https://example.com/updated_evo.png'  # Added
        }
        
        inserted2, updated2, errors2 = ingest_cards([updated_card])
        assert inserted2 == 0
        assert updated2 == 1
        assert errors2 == 0
        
        # Verify updated data
        cards_in_db = clean_database.execute_query(
            "SELECT * FROM cards WHERE id = %s", (26000040,)
        )
        assert len(cards_in_db) == 1  # Still only one record
        assert cards_in_db[0]['name'] == 'Updated Name'
        assert cards_in_db[0]['elixir_cost'] == 4
        assert cards_in_db[0]['rarity'] == 'Rare'
        assert cards_in_db[0]['arena'] == 'Arena 2'
        assert cards_in_db[0]['image_url_evo'] == 'https://example.com/updated_evo.png'
        
        # Verify total count is still 1
        count = clean_database.get_table_count('cards')
        assert count == 1
    
    def test_upsert_preserves_created_at(self, clean_database):
        """Test that upsert preserves the original created_at timestamp"""
        import time
        
        # Initial insert
        initial_card = {
            'id': 26000050,
            'name': 'Test Card',
            'elixir_cost': 3,
            'rarity': 'Common',
            'type': 'Troop',
            'arena': None,
            'image_url': 'https://example.com/test.png',
            'image_url_evo': None
        }
        
        inserted, updated, errors = ingest_cards([initial_card])
        assert inserted == 1
        
        # Get original timestamps
        cards_in_db = clean_database.execute_query(
            "SELECT created_at, updated_at FROM cards WHERE id = %s", (26000050,)
        )
        original_created_at = cards_in_db[0]['created_at']
        original_updated_at = cards_in_db[0]['updated_at']
        
        # Wait a moment to ensure timestamp difference
        time.sleep(1)
        
        # Update the card
        updated_card = {
            'id': 26000050,
            'name': 'Updated Test Card',
            'elixir_cost': 4,
            'rarity': 'Rare',
            'type': 'Troop',
            'arena': None,
            'image_url': 'https://example.com/test_updated.png',
            'image_url_evo': None
        }
        
        inserted2, updated2, errors2 = ingest_cards([updated_card])
        assert updated2 == 1
        
        # Get new timestamps
        cards_in_db = clean_database.execute_query(
            "SELECT created_at, updated_at FROM cards WHERE id = %s", (26000050,)
        )
        new_created_at = cards_in_db[0]['created_at']
        new_updated_at = cards_in_db[0]['updated_at']
        
        # created_at should be unchanged
        assert new_created_at == original_created_at
        
        # updated_at should be different (newer)
        assert new_updated_at > original_updated_at
    
    def test_batch_upsert_mixed_insert_and_update(self, clean_database):
        """Test batch upsert with mix of new and existing cards"""
        # Insert initial cards
        initial_cards = [
            {
                'id': 26000060,
                'name': 'Existing Card 1',
                'elixir_cost': 3,
                'rarity': 'Common',
                'type': 'Troop',
                'arena': None,
                'image_url': 'https://example.com/card1.png',
                'image_url_evo': None
            },
            {
                'id': 26000061,
                'name': 'Existing Card 2',
                'elixir_cost': 4,
                'rarity': 'Rare',
                'type': 'Troop',
                'arena': None,
                'image_url': 'https://example.com/card2.png',
                'image_url_evo': None
            }
        ]
        
        inserted, updated, errors = ingest_cards(initial_cards)
        assert inserted == 2
        assert updated == 0
        
        # Batch with mix of updates and new inserts
        mixed_batch = [
            {
                'id': 26000060,  # Existing - update
                'name': 'Updated Card 1',
                'elixir_cost': 5,
                'rarity': 'Epic',
                'type': 'Troop',
                'arena': None,
                'image_url': 'https://example.com/card1_updated.png',
                'image_url_evo': None
            },
            {
                'id': 26000062,  # New - insert
                'name': 'New Card 3',
                'elixir_cost': 2,
                'rarity': 'Common',
                'type': 'Troop',
                'arena': None,
                'image_url': 'https://example.com/card3.png',
                'image_url_evo': None
            },
            {
                'id': 26000061,  # Existing - update
                'name': 'Updated Card 2',
                'elixir_cost': 6,
                'rarity': 'Legendary',
                'type': 'Troop',
                'arena': None,
                'image_url': 'https://example.com/card2_updated.png',
                'image_url_evo': None
            }
        ]
        
        inserted2, updated2, errors2 = ingest_cards(mixed_batch)
        assert inserted2 == 1  # One new card
        assert updated2 == 2  # Two existing cards updated
        assert errors2 == 0
        
        # Verify total count
        count = clean_database.get_table_count('cards')
        assert count == 3
        
        # Verify updates
        card1 = clean_database.execute_query(
            "SELECT * FROM cards WHERE id = %s", (26000060,)
        )
        assert card1[0]['name'] == 'Updated Card 1'
        assert card1[0]['elixir_cost'] == 5
        
        card2 = clean_database.execute_query(
            "SELECT * FROM cards WHERE id = %s", (26000061,)
        )
        assert card2[0]['name'] == 'Updated Card 2'
        assert card2[0]['rarity'] == 'Legendary'
        
        card3 = clean_database.execute_query(
            "SELECT * FROM cards WHERE id = %s", (26000062,)
        )
        assert card3[0]['name'] == 'New Card 3'
