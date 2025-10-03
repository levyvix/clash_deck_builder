"""
Unit tests for card data ingestion script.

Tests the core functions of the ingestion script including:
- Card type determination based on ID ranges
- JSON data transformation to database schema
- JSON file loading and error handling
"""

import json
import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scripts.ingest_cards import (
    determine_card_type,
    transform_card_data,
    load_json_file
)


class TestDetermineCardType:
    """Tests for determine_card_type() function."""
    
    def test_troop_id_range_lower_bound(self):
        """Test that ID 26000000 is classified as Troop."""
        assert determine_card_type(26000000) == 'Troop'
    
    def test_troop_id_range_middle(self):
        """Test that ID in middle of Troop range is classified as Troop."""
        assert determine_card_type(26500000) == 'Troop'
    
    def test_troop_id_range_upper_bound(self):
        """Test that ID 26999999 is classified as Troop."""
        assert determine_card_type(26999999) == 'Troop'
    
    def test_building_id_range_lower_bound(self):
        """Test that ID 27000000 is classified as Building."""
        assert determine_card_type(27000000) == 'Building'
    
    def test_building_id_range_middle(self):
        """Test that ID in middle of Building range is classified as Building."""
        assert determine_card_type(27500000) == 'Building'
    
    def test_building_id_range_upper_bound(self):
        """Test that ID 27999999 is classified as Building."""
        assert determine_card_type(27999999) == 'Building'
    
    def test_spell_id_range_lower_bound(self):
        """Test that ID 28000000 is classified as Spell."""
        assert determine_card_type(28000000) == 'Spell'
    
    def test_spell_id_range_middle(self):
        """Test that ID in middle of Spell range is classified as Spell."""
        assert determine_card_type(28500000) == 'Spell'
    
    def test_spell_id_range_upper_bound(self):
        """Test that ID 28999999 is classified as Spell."""
        assert determine_card_type(28999999) == 'Spell'
    
    def test_unknown_id_defaults_to_troop(self):
        """Test that unknown ID ranges default to Troop."""
        assert determine_card_type(99999999) == 'Troop'
        assert determine_card_type(1000) == 'Troop'


class TestTransformCardData:
    """Tests for transform_card_data() function."""
    
    def test_transform_complete_json_data(self):
        """Test transformation with all fields present."""
        card_json = {
            'id': 26000001,
            'name': 'Knight',
            'elixirCost': 3,
            'rarity': 'common',
            'arena': {'name': 'Training Camp'},
            'iconUrls': {
                'medium': 'https://api-assets.clashroyale.com/cards/300/knight.png',
                'evolutionMedium': 'https://api-assets.clashroyale.com/cards/300/knight_evo.png'
            }
        }
        
        result = transform_card_data(card_json)
        
        assert result is not None
        assert result['id'] == 26000001
        assert result['name'] == 'Knight'
        assert result['elixir_cost'] == 3
        assert result['rarity'] == 'Common'
        assert result['type'] == 'Troop'
        assert result['arena'] == 'Training Camp'
        assert result['image_url'] == 'https://api-assets.clashroyale.com/cards/300/knight.png'
        assert result['image_url_evo'] == 'https://api-assets.clashroyale.com/cards/300/knight_evo.png'
    
    def test_transform_missing_optional_fields(self):
        """Test transformation with missing optional fields (arena, image_url_evo)."""
        card_json = {
            'id': 27000001,
            'name': 'Cannon',
            'elixirCost': 3,
            'rarity': 'common',
            'iconUrls': {
                'medium': 'https://api-assets.clashroyale.com/cards/300/cannon.png'
            }
        }
        
        result = transform_card_data(card_json)
        
        assert result is not None
        assert result['id'] == 27000001
        assert result['name'] == 'Cannon'
        assert result['elixir_cost'] == 3
        assert result['rarity'] == 'Common'
        assert result['type'] == 'Building'
        assert result['arena'] is None
        assert result['image_url'] == 'https://api-assets.clashroyale.com/cards/300/cannon.png'
        assert result['image_url_evo'] is None
    
    def test_transform_rarity_normalization(self):
        """Test that rarity values are normalized to Title Case."""
        test_cases = [
            ('common', 'Common'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary'),
            ('champion', 'Champion')
        ]
        
        for input_rarity, expected_rarity in test_cases:
            card_json = {
                'id': 26000001,
                'name': 'Test Card',
                'elixirCost': 3,
                'rarity': input_rarity,
                'iconUrls': {
                    'medium': 'https://example.com/card.png'
                }
            }
            
            result = transform_card_data(card_json)
            assert result['rarity'] == expected_rarity
    
    def test_transform_missing_id(self):
        """Test that cards without ID are skipped."""
        card_json = {
            'name': 'Invalid Card',
            'elixirCost': 3,
            'rarity': 'common',
            'iconUrls': {
                'medium': 'https://example.com/card.png'
            }
        }
        
        result = transform_card_data(card_json)
        assert result is None
    
    def test_transform_missing_name(self):
        """Test that cards without name are skipped."""
        card_json = {
            'id': 26000001,
            'elixirCost': 3,
            'rarity': 'common',
            'iconUrls': {
                'medium': 'https://example.com/card.png'
            }
        }
        
        result = transform_card_data(card_json)
        assert result is None
    
    def test_transform_missing_elixir_cost(self):
        """Test that cards without elixir cost are skipped."""
        card_json = {
            'id': 26000001,
            'name': 'Invalid Card',
            'rarity': 'common',
            'iconUrls': {
                'medium': 'https://example.com/card.png'
            }
        }
        
        result = transform_card_data(card_json)
        assert result is None
    
    def test_transform_missing_rarity(self):
        """Test that cards without rarity are skipped."""
        card_json = {
            'id': 26000001,
            'name': 'Invalid Card',
            'elixirCost': 3,
            'iconUrls': {
                'medium': 'https://example.com/card.png'
            }
        }
        
        result = transform_card_data(card_json)
        assert result is None
    
    def test_transform_missing_image_url(self):
        """Test that cards without image URL are skipped."""
        card_json = {
            'id': 26000001,
            'name': 'Invalid Card',
            'elixirCost': 3,
            'rarity': 'common',
            'iconUrls': {}
        }
        
        result = transform_card_data(card_json)
        assert result is None
    
    def test_transform_arena_as_string(self):
        """Test transformation when arena is a string instead of dict."""
        card_json = {
            'id': 26000001,
            'name': 'Knight',
            'elixirCost': 3,
            'rarity': 'common',
            'arena': 'Training Camp',
            'iconUrls': {
                'medium': 'https://example.com/card.png'
            }
        }
        
        result = transform_card_data(card_json)
        assert result is not None
        assert result['arena'] == 'Training Camp'
    
    def test_transform_spell_card(self):
        """Test transformation of a Spell card (ID range 28000000-28999999)."""
        card_json = {
            'id': 28000001,
            'name': 'Fireball',
            'elixirCost': 4,
            'rarity': 'rare',
            'iconUrls': {
                'medium': 'https://example.com/fireball.png'
            }
        }
        
        result = transform_card_data(card_json)
        assert result is not None
        assert result['type'] == 'Spell'


class TestLoadJsonFile:
    """Tests for load_json_file() function."""
    
    def test_load_valid_json_file(self):
        """Test loading a valid JSON file."""
        valid_json = {
            'items': [
                {
                    'id': 26000001,
                    'name': 'Knight',
                    'elixirCost': 3,
                    'rarity': 'common'
                }
            ]
        }
        
        mock_file_content = json.dumps(valid_json)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            result = load_json_file('test_file.json')
            
            assert result == valid_json
            assert 'items' in result
            assert len(result['items']) == 1
            assert result['items'][0]['name'] == 'Knight'
    
    def test_load_json_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                load_json_file('nonexistent.json')
    
    def test_load_invalid_json(self):
        """Test that JSONDecodeError is raised for invalid JSON."""
        invalid_json = "{ invalid json content"
        
        with patch('builtins.open', mock_open(read_data=invalid_json)):
            with pytest.raises(json.JSONDecodeError):
                load_json_file('invalid.json')
    
    def test_load_empty_json_file(self):
        """Test loading an empty JSON object."""
        empty_json = "{}"
        
        with patch('builtins.open', mock_open(read_data=empty_json)):
            result = load_json_file('empty.json')
            
            assert result == {}
    
    def test_load_json_with_multiple_cards(self):
        """Test loading JSON with multiple cards."""
        multi_card_json = {
            'items': [
                {'id': 26000001, 'name': 'Knight'},
                {'id': 26000002, 'name': 'Archers'},
                {'id': 27000001, 'name': 'Cannon'}
            ]
        }
        
        mock_file_content = json.dumps(multi_card_json)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            result = load_json_file('cards.json')
            
            assert len(result['items']) == 3
            assert result['items'][0]['name'] == 'Knight'
            assert result['items'][1]['name'] == 'Archers'
            assert result['items'][2]['name'] == 'Cannon'
