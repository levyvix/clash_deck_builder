-- backend/src/models/schema.sql
-- Clash Royale Deck Builder Database Schema

-- Users table for future authentication support
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_users_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Decks table with proper constraints and relationships
CREATE TABLE IF NOT EXISTS decks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INT DEFAULT NULL,
    cards JSON NOT NULL,
    evolution_slots JSON DEFAULT NULL,
    average_elixir DECIMAL(4,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_deck_name_length CHECK (CHAR_LENGTH(name) >= 1 AND CHAR_LENGTH(name) <= 255),
    CONSTRAINT chk_average_elixir CHECK (average_elixir >= 0.00 AND average_elixir <= 10.00),
    CONSTRAINT chk_cards_not_empty CHECK (JSON_LENGTH(cards) > 0),
    CONSTRAINT chk_cards_max_count CHECK (JSON_LENGTH(cards) <= 8),
    CONSTRAINT chk_evolution_slots_max_count CHECK (evolution_slots IS NULL OR JSON_LENGTH(evolution_slots) <= 2),
    
    -- Foreign key relationship
    CONSTRAINT fk_decks_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes for performance optimization
    INDEX idx_decks_user_id (user_id),
    INDEX idx_decks_name (name),
    INDEX idx_decks_created_at (created_at),
    INDEX idx_decks_average_elixir (average_elixir),
    INDEX idx_decks_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional cards table for caching Clash Royale API data locally
-- This can improve performance and reduce API calls
CREATE TABLE IF NOT EXISTS cards (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    elixir_cost INT NOT NULL,
    rarity ENUM('Common', 'Rare', 'Epic', 'Legendary', 'Champion') NOT NULL,
    type ENUM('Troop', 'Spell', 'Building') NOT NULL,
    arena VARCHAR(100) DEFAULT NULL,
    image_url VARCHAR(500) NOT NULL,
    image_url_evo VARCHAR(500) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_card_name_length CHECK (CHAR_LENGTH(name) >= 1 AND CHAR_LENGTH(name) <= 255),
    CONSTRAINT chk_elixir_cost CHECK (elixir_cost >= 0 AND elixir_cost <= 10),
    CONSTRAINT chk_image_url_length CHECK (CHAR_LENGTH(image_url) >= 1 AND CHAR_LENGTH(image_url) <= 500),
    
    -- Indexes for performance optimization
    INDEX idx_cards_name (name),
    INDEX idx_cards_elixir_cost (elixir_cost),
    INDEX idx_cards_rarity (rarity),
    INDEX idx_cards_type (type),
    INDEX idx_cards_arena (arena),
    INDEX idx_cards_rarity_type (rarity, type),
    INDEX idx_cards_elixir_rarity (elixir_cost, rarity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Trigger to automatically update the updated_at timestamp
DELIMITER $$

CREATE TRIGGER IF NOT EXISTS tr_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER IF NOT EXISTS tr_decks_updated_at
    BEFORE UPDATE ON decks
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER IF NOT EXISTS tr_cards_updated_at
    BEFORE UPDATE ON cards
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

DELIMITER ;

-- Insert a default user for development/testing purposes
INSERT IGNORE INTO users (id) VALUES (1);
