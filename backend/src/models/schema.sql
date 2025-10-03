-- backend/src/models/schema.sql

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- Add other user-related fields here if necessary
);

CREATE TABLE IF NOT EXISTS decks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INT,
    -- Cards will be stored as JSON or in a separate join table
    -- For now, a simple JSON representation:
    cards JSON,
    evolution_slots JSON,
    average_elixir FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add a table for cards if we decide to cache them locally
-- CREATE TABLE IF NOT EXISTS cards (
--    id INT PRIMARY KEY,
--    name VARCHAR(255) NOT NULL,
--    elixir_cost INT,
--    rarity VARCHAR(50),
--    type VARCHAR(50),
--    arena VARCHAR(50),
--    image_url VARCHAR(255)
-- );
