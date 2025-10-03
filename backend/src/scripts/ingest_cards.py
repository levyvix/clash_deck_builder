#!/usr/bin/env python3
"""
Card Data Ingestion Script

This script loads card data from all_cards.json and ingests it into the MySQL database.
It handles card type detection, data transformation, and upsert operations.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.database import db_manager, DatabaseError
from src.utils.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> dict:
    """
    Load and parse the JSON file containing card data.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        logger.info(f"Loading JSON file from: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded JSON file with {len(data.get('items', []))} cards")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading JSON file: {e}")
        raise


def determine_card_type(card_id: int) -> str:
    """
    Determine card type based on ID range.
    
    ID Ranges:
    - 26000000-26999999: Troop
    - 27000000-27999999: Building
    - 28000000-28999999: Spell
    
    Args:
        card_id: The card's unique identifier
        
    Returns:
        Card type as string ('Troop', 'Building', or 'Spell')
    """
    if 26000000 <= card_id <= 26999999:
        return 'Troop'
    elif 27000000 <= card_id <= 27999999:
        return 'Building'
    elif 28000000 <= card_id <= 28999999:
        return 'Spell'
    else:
        logger.warning(f"Card ID {card_id} doesn't match known ranges, defaulting to 'Troop'")
        return 'Troop'


def transform_card_data(card_json: dict) -> Optional[dict]:
    """
    Transform JSON card data to database schema format.
    
    Maps JSON fields to database columns:
    - elixirCost → elixir_cost
    - iconUrls.medium → image_url
    - iconUrls.evolutionMedium → image_url_evo
    - rarity (lowercase → Title Case)
    
    Args:
        card_json: Card data from JSON file
        
    Returns:
        Dictionary with database column names and values, or None if invalid
    """
    try:
        card_id = card_json.get('id')
        if not card_id:
            logger.warning(f"Card missing ID, skipping: {card_json.get('name', 'Unknown')}")
            return None
        
        # Extract required fields
        name = card_json.get('name')
        elixir_cost = card_json.get('elixirCost')
        rarity = card_json.get('rarity', '').lower()
        
        if not all([name, elixir_cost is not None, rarity]):
            logger.warning(f"Card {card_id} missing required fields, skipping")
            return None
        
        # Normalize rarity to Title Case
        rarity_map = {
            'common': 'Common',
            'rare': 'Rare',
            'epic': 'Epic',
            'legendary': 'Legendary',
            'champion': 'Champion'
        }
        rarity_normalized = rarity_map.get(rarity, rarity.title())
        
        # Determine card type from ID
        card_type = determine_card_type(card_id)
        
        # Extract image URLs
        icon_urls = card_json.get('iconUrls', {})
        image_url = icon_urls.get('medium')
        image_url_evo = icon_urls.get('evolutionMedium')
        
        if not image_url:
            logger.warning(f"Card {card_id} ({name}) missing image URL, skipping")
            return None
        
        # Extract arena (optional)
        arena = None
        if 'arena' in card_json and card_json['arena']:
            if isinstance(card_json['arena'], dict):
                arena = card_json['arena'].get('name')
            else:
                arena = str(card_json['arena'])
        
        return {
            'id': card_id,
            'name': name,
            'elixir_cost': elixir_cost,
            'rarity': rarity_normalized,
            'type': card_type,
            'arena': arena,
            'image_url': image_url,
            'image_url_evo': image_url_evo
        }
        
    except Exception as e:
        logger.error(f"Error transforming card data: {e}")
        return None


def ingest_cards(cards_data: List[dict]) -> Tuple[int, int, int]:
    """
    Insert or update cards in the database using upsert logic.
    
    Uses INSERT ... ON DUPLICATE KEY UPDATE to handle both new cards
    and updates to existing cards.
    
    Args:
        cards_data: List of transformed card dictionaries
        
    Returns:
        Tuple of (inserted_count, updated_count, error_count)
        
    Raises:
        DatabaseError: If database operations fail
    """
    inserted_count = 0
    updated_count = 0
    error_count = 0
    
    # SQL for upsert operation (using modern MySQL 8.0+ syntax with alias)
    upsert_sql = """
        INSERT INTO cards (
            id, name, elixir_cost, rarity, type, arena, image_url, image_url_evo
        ) VALUES (
            %(id)s, %(name)s, %(elixir_cost)s, %(rarity)s, %(type)s, %(arena)s, %(image_url)s, %(image_url_evo)s
        ) AS new_card
        ON DUPLICATE KEY UPDATE
            name = new_card.name,
            elixir_cost = new_card.elixir_cost,
            rarity = new_card.rarity,
            type = new_card.type,
            arena = new_card.arena,
            image_url = new_card.image_url,
            image_url_evo = new_card.image_url_evo,
            updated_at = CURRENT_TIMESTAMP
    """
    
    try:
        # Initialize database connection
        db_manager.initialize()
        
        logger.info(f"Starting ingestion of {len(cards_data)} cards")
        
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            
            try:
                # Process cards in batches for better performance
                batch_size = 50
                for i in range(0, len(cards_data), batch_size):
                    batch = cards_data[i:i + batch_size]
                    
                    for card in batch:
                        try:
                            # Check if card exists before insert
                            cursor.execute("SELECT id FROM cards WHERE id = %s", (card['id'],))
                            exists = cursor.fetchone() is not None
                            
                            # Execute upsert
                            cursor.execute(upsert_sql, card)
                            
                            # Track whether this was an insert or update
                            if exists:
                                updated_count += 1
                            else:
                                inserted_count += 1
                                
                        except Exception as e:
                            error_count += 1
                            logger.error(f"Error processing card {card.get('id')} ({card.get('name')}): {e}")
                            continue
                    
                    # Commit batch
                    connection.commit()
                    logger.info(f"Processed batch {i//batch_size + 1} ({i + len(batch)}/{len(cards_data)} cards)")
                
                logger.info(f"Ingestion complete: {inserted_count} inserted, {updated_count} updated, {error_count} errors")
                
            except Exception as e:
                connection.rollback()
                logger.error(f"Transaction failed, rolling back: {e}")
                raise DatabaseError(f"Failed to ingest cards: {e}")
            finally:
                cursor.close()
                
    except DatabaseError as e:
        logger.error(f"Database error during ingestion: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {e}")
        raise DatabaseError(f"Unexpected error during ingestion: {e}")
    
    return inserted_count, updated_count, error_count


def main():
    """Main execution function."""
    try:
        logger.info("=" * 60)
        logger.info("Starting Card Data Ingestion")
        logger.info("=" * 60)
        
        # Get settings
        settings = get_settings()
        logger.info(f"Database: {settings.db_name} at {settings.db_host}:{settings.db_port}")
        
        # Determine path to all_cards.json (in project root)
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent.parent
        json_file_path = project_root / 'all_cards.json'
        
        # Load JSON file
        data = load_json_file(str(json_file_path))
        cards_list = data.get('items', [])
        
        if not cards_list:
            logger.warning("No cards found in JSON file")
            return 0
        
        logger.info(f"Found {len(cards_list)} cards in JSON file")
        
        # Transform card data
        logger.info("Transforming card data...")
        transformed_cards = []
        for card_json in cards_list:
            transformed = transform_card_data(card_json)
            if transformed:
                transformed_cards.append(transformed)
        
        logger.info(f"Successfully transformed {len(transformed_cards)} cards")
        
        if not transformed_cards:
            logger.error("No valid cards to ingest")
            return 1
        
        # Ingest cards into database
        logger.info("Ingesting cards into database...")
        inserted, updated, errors = ingest_cards(transformed_cards)
        
        # Summary
        logger.info("=" * 60)
        logger.info("Ingestion Summary:")
        logger.info(f"  Total cards processed: {len(transformed_cards)}")
        logger.info(f"  Cards inserted: {inserted}")
        logger.info(f"  Cards updated: {updated}")
        logger.info(f"  Errors: {errors}")
        logger.info("=" * 60)
        
        if errors > 0:
            logger.warning(f"Completed with {errors} errors")
            return 1
        
        logger.info("Card data ingestion completed successfully!")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return 1
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
