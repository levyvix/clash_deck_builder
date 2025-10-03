-- Performance indexes for Clash Royale Deck Builder database
-- These indexes optimize common query patterns for better performance

-- Users table indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Decks table indexes for common query patterns
CREATE INDEX idx_decks_user_id ON decks(user_id);
CREATE INDEX idx_decks_name ON decks(name);
CREATE INDEX idx_decks_created_at ON decks(created_at);
CREATE INDEX idx_decks_updated_at ON decks(updated_at);
CREATE INDEX idx_decks_average_elixir ON decks(average_elixir);

-- Composite indexes for common multi-column queries
CREATE INDEX idx_decks_user_created ON decks(user_id, created_at);
CREATE INDEX idx_decks_user_name ON decks(user_id, name);

-- Cards cache table indexes for filtering and searching
CREATE INDEX idx_cards_cache_name ON cards_cache(name);
CREATE INDEX idx_cards_cache_rarity ON cards_cache(rarity);
CREATE INDEX idx_cards_cache_elixir_cost ON cards_cache(elixir_cost);
CREATE INDEX idx_cards_cache_type ON cards_cache(type);
CREATE INDEX idx_cards_cache_arena ON cards_cache(arena);
CREATE INDEX idx_cards_cache_last_updated ON cards_cache(last_updated);

-- Composite indexes for common filtering combinations
CREATE INDEX idx_cards_cache_rarity_elixir ON cards_cache(rarity, elixir_cost);
CREATE INDEX idx_cards_cache_type_elixir ON cards_cache(type, elixir_cost);
CREATE INDEX idx_cards_cache_rarity_type ON cards_cache(rarity, type);

-- Full-text search index for card names (for search functionality)
CREATE FULLTEXT INDEX idx_cards_cache_name_fulltext ON cards_cache(name);

-- Index comments for documentation
-- User indexes: Optimize user lookup and authentication queries
-- Deck indexes: Optimize deck listing, filtering by user, and sorting operations
-- Card cache indexes: Optimize card filtering, searching, and API data refresh operations
-- Composite indexes: Optimize complex queries that filter on multiple columns simultaneously