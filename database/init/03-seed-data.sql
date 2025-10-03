-- Development seed data for Clash Royale Deck Builder
-- This script populates the database with sample data for development and testing

-- Insert test users
INSERT IGNORE INTO users (id, username, email, created_at) VALUES
(1, 'testuser1', 'testuser1@example.com', '2024-01-01 10:00:00'),
(2, 'deckmaster', 'deckmaster@example.com', '2024-01-02 11:00:00'),
(3, 'clashpro', 'clashpro@example.com', '2024-01-03 12:00:00');

-- Insert sample card data (subset of popular Clash Royale cards)
INSERT IGNORE INTO cards_cache (id, name, elixir_cost, rarity, type, arena, image_url, image_url_evo) VALUES
-- Troops
(26000000, 'Knight', 3, 'Common', 'Troop', 'Training Camp', 'https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png', NULL),
(26000001, 'Archers', 3, 'Common', 'Troop', 'Training Camp', 'https://api-assets.clashroyale.com/cards/300/W72-7h2jdHjAAOjMDQrqAEYVHdXR0WcOqKEYZFJCQgw.png', NULL),
(26000002, 'Goblins', 2, 'Common', 'Troop', 'Goblin Stadium', 'https://api-assets.clashroyale.com/cards/300/D7b7jPiNcF0fNw7T_-qMcKYHMu0a3GgKeuNofjNjGe0.png', NULL),
(26000003, 'Giant', 5, 'Rare', 'Troop', 'Bone Pit', 'https://api-assets.clashroyale.com/cards/300/npdcVJeZnNGl8OaLaGmVbZc1Oj_QqjhEhc6LAe6_cnw.png', NULL),
(26000004, 'P.E.K.K.A', 7, 'Epic', 'Troop', 'P.E.K.K.A Playhouse', 'https://api-assets.clashroyale.com/cards/300/MlArURKhn_zWAZY-Xj1qIRKLVKquQ5Ej0nWUYe8XHT4.png', NULL),
(26000005, 'Minions', 3, 'Common', 'Troop', 'Spell Valley', 'https://api-assets.clashroyale.com/cards/300/yHGpoEnmUWPGV_hBbhn-Kk1wtvfaJjbf2yElPW0wusw.png', NULL),
(26000006, 'Balloon', 5, 'Epic', 'Troop', 'Balloon Lagoon', 'https://api-assets.clashroyale.com/cards/300/9IngUBU_RKIeqKING1hTz2-iMjrI_xTIzt5DqJsAiH4.png', NULL),
(26000007, 'Wizard', 5, 'Rare', 'Troop', 'Spell Valley', 'https://api-assets.clashroyale.com/cards/300/Hqx1p72XMGX6hsYeV7kwMwrBTmX89jLz8SzNLjJQKQ0.png', NULL),
(26000008, 'Dragon', 4, 'Epic', 'Troop', 'Training Camp', 'https://api-assets.clashroyale.com/cards/300/l4cqOV1ZulyKqspBG7dL7of4-M6BkpNtCkRmb8yiQUc.png', NULL),
(26000009, 'Musketeer', 4, 'Rare', 'Troop', 'Bone Pit', 'https://api-assets.clashroyale.com/cards/300/Tex1C48UTq9FqjKl_5tpEQzfsAuOVbFqUVZjKdM6qGI.png', NULL),

-- Spells
(28000000, 'Fireball', 4, 'Rare', 'Spell', 'Bone Pit', 'https://api-assets.clashroyale.com/cards/300/lZD9MIc8gQ2ckUhqOGD_Q5C_ZzJmBjzeGlFSzpOq2mg.png', NULL),
(28000001, 'Arrows', 3, 'Common', 'Spell', 'Goblin Stadium', 'https://api-assets.clashroyale.com/cards/300/droNVEOdOkVjHQjYHVWNDVaE0Y8VRKQM-yZuod10yQI.png', NULL),
(28000002, 'Zap', 2, 'Common', 'Spell', 'Electro Valley', 'https://api-assets.clashroyale.com/cards/300/7Rt7Cp5efNWGNhEaRbKUqKKOJ_zyAhYbOl_jCkz8z2s.png', NULL),
(28000003, 'Lightning', 6, 'Epic', 'Spell', 'Electro Valley', 'https://api-assets.clashroyale.com/cards/300/fpOOUb1cP7xUBpsAEpK7LKXNNjGU_55hzTSGdhQaO8E.png', NULL),
(28000004, 'Rage', 2, 'Epic', 'Spell', 'Arena 6', 'https://api-assets.clashroyale.com/cards/300/S677QXNnEhHuo3d4H4cIjWQXp1Q3YsN-F_S4xGoqM-E.png', NULL),

-- Buildings
(27000000, 'Cannon', 3, 'Common', 'Building', 'Goblin Stadium', 'https://api-assets.clashroyale.com/cards/300/Jh6G7AQi2pGGmyJiLCoOjmczMt_4nSBNwpOOGHOhD-s.png', NULL),
(27000001, 'Tesla', 4, 'Common', 'Building', 'P.E.K.K.A Playhouse', 'https://api-assets.clashroyale.com/cards/300/OiwneyPSDJ5nCtyrGD_MS7w0P5uGa2k6ranBdJKNiNs.png', NULL),
(27000002, 'Inferno Tower', 5, 'Rare', 'Building', 'P.E.K.K.A Playhouse', 'https://api-assets.clashroyale.com/cards/300/r9hK_g7NKBIjdppg_c4OjGX5fKOqzAAu2k0vEuFnqpE.png', NULL),
(27000003, 'Bomb Tower', 4, 'Rare', 'Building', 'Bone Pit', 'https://api-assets.clashroyale.com/cards/300/lZD9MIc8gQ2ckUhqOGD_Q5C_ZzJmBjzeGlFSzpOq2mg.png', NULL),

-- Legendary Cards
(26000010, 'Princess', 3, 'Legendary', 'Troop', 'Royal Arena', 'https://api-assets.clashroyale.com/cards/300/150y_147CaWaVaVblFh_lZIrUeMNjFz4WmLaOoOjUzI.png', NULL),
(26000011, 'Ice Wizard', 3, 'Legendary', 'Troop', 'Frozen Peak', 'https://api-assets.clashroyale.com/cards/300/W72-7h2jdHjAAOjMDQrqAEYVHdXR0WcOqKEYZFJCQgw.png', NULL),
(26000012, 'Lava Hound', 7, 'Legendary', 'Troop', 'Frozen Peak', 'https://api-assets.clashroyale.com/cards/300/9IngUBU_RKIeqKING1hTz2-iMjrI_xTIzt5DqJsAiH4.png', NULL);

-- Insert sample decks for test users
INSERT IGNORE INTO decks (id, name, user_id, cards, evolution_slots, average_elixir, created_at) VALUES
(1, 'Classic Hog Cycle', 1, 
 '[{"id": 26000000, "name": "Knight"}, {"id": 26000001, "name": "Archers"}, {"id": 26000002, "name": "Goblins"}, {"id": 28000000, "name": "Fireball"}, {"id": 28000001, "name": "Arrows"}, {"id": 28000002, "name": "Zap"}, {"id": 27000000, "name": "Cannon"}, {"id": 26000009, "name": "Musketeer"}]',
 '[]', 3.25, '2024-01-01 15:00:00'),

(2, 'Giant Beatdown', 1,
 '[{"id": 26000003, "name": "Giant"}, {"id": 26000007, "name": "Wizard"}, {"id": 26000009, "name": "Musketeer"}, {"id": 26000005, "name": "Minions"}, {"id": 28000000, "name": "Fireball"}, {"id": 28000002, "name": "Zap"}, {"id": 27000001, "name": "Tesla"}, {"id": 26000001, "name": "Archers"}]',
 '[{"id": 26000003, "name": "Giant"}]', 4.0, '2024-01-01 16:00:00'),

(3, 'P.E.K.K.A Control', 2,
 '[{"id": 26000004, "name": "P.E.K.K.A"}, {"id": 26000007, "name": "Wizard"}, {"id": 26000009, "name": "Musketeer"}, {"id": 28000000, "name": "Fireball"}, {"id": 28000003, "name": "Lightning"}, {"id": 28000002, "name": "Zap"}, {"id": 27000002, "name": "Inferno Tower"}, {"id": 26000001, "name": "Archers"}]',
 '[{"id": 26000004, "name": "P.E.K.K.A"}, {"id": 26000007, "name": "Wizard"}]', 4.75, '2024-01-02 14:00:00'),

(4, 'Balloon Freeze', 2,
 '[{"id": 26000006, "name": "Balloon"}, {"id": 26000005, "name": "Minions"}, {"id": 26000002, "name": "Goblins"}, {"id": 28000004, "name": "Rage"}, {"id": 28000001, "name": "Arrows"}, {"id": 28000002, "name": "Zap"}, {"id": 27000000, "name": "Cannon"}, {"id": 26000000, "name": "Knight"}]',
 '[]', 3.5, '2024-01-02 15:30:00'),

(5, 'Legendary Deck', 3,
 '[{"id": 26000010, "name": "Princess"}, {"id": 26000011, "name": "Ice Wizard"}, {"id": 26000012, "name": "Lava Hound"}, {"id": 26000005, "name": "Minions"}, {"id": 28000000, "name": "Fireball"}, {"id": 28000002, "name": "Zap"}, {"id": 27000001, "name": "Tesla"}, {"id": 26000001, "name": "Archers"}]',
 '[{"id": 26000010, "name": "Princess"}]', 4.25, '2024-01-03 13:00:00');

-- Update last_updated timestamp for cards_cache to simulate recent API sync
UPDATE cards_cache SET last_updated = NOW() WHERE id IN (26000000, 26000001, 26000002);