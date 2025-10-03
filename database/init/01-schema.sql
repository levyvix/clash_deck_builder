-- Database schema initialization for Clash Royale Deck Builder
-- This script creates the core tables with proper constraints and relationships

-- Users table for future authentication and deck ownership
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_username_length CHECK (CHAR_LENGTH(username) >= 3),
    CONSTRAINT chk_email_format CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Decks table for storing user-created decks
CREATE TABLE IF NOT EXISTS decks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INT,
    cards JSON NOT NULL,
    evolution_slots JSON,
    average_elixir DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_deck_name_length CHECK (CHAR_LENGTH(name) >= 1),
    CONSTRAINT chk_average_elixir_range CHECK (average_elixir >= 0.0 AND average_elixir <= 10.0),
    CONSTRAINT chk_cards_not_empty CHECK (JSON_LENGTH(cards) > 0),
    CONSTRAINT chk_evolution_slots_limit CHECK (JSON_LENGTH(evolution_slots) <= 2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cards table for storing Clash Royale card data
CREATE TABLE IF NOT EXISTS cards (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    elixir_cost INT NOT NULL,
    rarity VARCHAR(20) NOT NULL,
    type VARCHAR(20) NOT NULL,
    arena VARCHAR(50),
    image_url TEXT NOT NULL,
    image_url_evo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_cards_elixir_cost_range CHECK (elixir_cost >= 0 AND elixir_cost <= 10),
    CONSTRAINT chk_cards_rarity_values CHECK (rarity IN ('Common', 'Rare', 'Epic', 'Legendary', 'Champion')),
    CONSTRAINT chk_cards_type_values CHECK (type IN ('Troop', 'Spell', 'Building')),
    CONSTRAINT chk_cards_name_not_empty CHECK (CHAR_LENGTH(name) > 0),
    CONSTRAINT chk_cards_image_url_not_empty CHECK (CHAR_LENGTH(image_url) > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cards cache table for storing Clash Royale API data
CREATE TABLE IF NOT EXISTS cards_cache (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    elixir_cost INT NOT NULL,
    rarity VARCHAR(20) NOT NULL,
    type VARCHAR(20) NOT NULL,
    arena VARCHAR(50),
    image_url TEXT NOT NULL,
    image_url_evo TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_cache_elixir_cost_range CHECK (elixir_cost >= 0 AND elixir_cost <= 10),
    CONSTRAINT chk_cache_rarity_values CHECK (rarity IN ('Common', 'Rare', 'Epic', 'Legendary', 'Champion')),
    CONSTRAINT chk_cache_type_values CHECK (type IN ('Troop', 'Spell', 'Building')),
    CONSTRAINT chk_cache_name_not_empty CHECK (CHAR_LENGTH(name) > 0),
    CONSTRAINT chk_cache_image_url_not_empty CHECK (CHAR_LENGTH(image_url) > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add comments for documentation
ALTER TABLE users COMMENT = 'User accounts for deck ownership and future authentication';
ALTER TABLE decks COMMENT = 'User-created Clash Royale decks with card compositions and metadata';
ALTER TABLE cards COMMENT = 'Primary card data table for Clash Royale cards';
ALTER TABLE cards_cache COMMENT = 'Cached card data from Clash Royale API for performance optimization';