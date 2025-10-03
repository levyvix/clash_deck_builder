-- Test data for integration testing
-- This file contains minimal test data for running integration tests

-- Insert test users
INSERT INTO users (id, username, email, created_at, updated_at) VALUES
(1, 'test_user_1', 'test1@example.com', '2024-01-01 10:00:00', '2024-01-01 10:00:00'),
(2, 'test_user_2', 'test2@example.com', '2024-01-01 11:00:00', '2024-01-01 11:00:00'),
(3, 'test_user_3', 'test3@example.com', '2024-01-01 12:00:00', '2024-01-01 12:00:00');

-- Insert test cards cache data
INSERT INTO cards_cache (id, name, elixir_cost, rarity, type, arena, image_url, image_url_evo, last_updated) VALUES
(26000000, 'Knight', 3, 'Common', 'Troop', 'Training Camp', 'https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png', NULL, '2024-01-01 10:00:00'),
(26000001, 'Archers', 3, 'Common', 'Troop', 'Training Camp', 'https://api-assets.clashroyale.com/cards/300/W84poW3tC9QQd-8sbzF2o4jrWzKZj0CvEPqVN2Fy_SY.png', NULL, '2024-01-01 10:00:00'),
(26000002, 'Goblins', 2, 'Common', 'Troop', 'Goblin Stadium', 'https://api-assets.clashroyale.com/cards/300/D7b7jPiOmJaWi-wWts-DzWG8sjmU2_MqTitvhXOZWKE.png', NULL, '2024-01-01 10:00:00'),
(26000003, 'Giant', 5, 'Rare', 'Troop', 'Training Camp', 'https://api-assets.clashroyale.com/cards/300/npdcVJCZY6NQ_1JWMdwNqbBrXEchAm8uoUAaKqgFCfE.png', NULL, '2024-01-01 10:00:00'),
(26000004, 'P.E.K.K.A', 7, 'Epic', 'Troop', 'P.E.K.K.As Playhouse', 'https://api-assets.clashroyale.com/cards/300/MlArURKhn_zWAZY-Xj1qIRKLVKquQ5Ej7hNwrEVbpjw.png', NULL, '2024-01-01 10:00:00'),
(26000005, 'Minions', 3, 'Common', 'Troop', 'Goblin Stadium', 'https://api-assets.clashroyale.com/cards/300/yHGpoEnmUWPGV_hBOaOnyWJA3lrTBk5KGqfLgUbCj2E.png', NULL, '2024-01-01 10:00:00'),
(26000006, 'Balloon', 5, 'Epic', 'Troop', 'Bone Pit', 'https://api-assets.clashroyale.com/cards/300/9CMKwkZg1hbJGmNzl0z0gyV0Jg8uOOfosjCsYIkUaQI.png', NULL, '2024-01-01 10:00:00'),
(26000007, 'Witch', 5, 'Epic', 'Troop', 'P.E.K.K.As Playhouse', 'https://api-assets.clashroyale.com/cards/300/cfwk1vzehVyHC-uloEIH6NOI0hOdofCutR5PyhIgSMo.png', NULL, '2024-01-01 10:00:00'),
(28000000, 'Fireball', 4, 'Rare', 'Spell', 'Goblin Stadium', 'https://api-assets.clashroyale.com/cards/300/lZD6hp7STYaM0H5kcE6aOr-wrwmOzDAeaE3jYQpyqQI.png', NULL, '2024-01-01 10:00:00'),
(28000001, 'Arrows', 3, 'Common', 'Spell', 'Training Camp', 'https://api-assets.clashroyale.com/cards/300/DtuJRmwJf2ch-GyGLBdUhT-DqUzMJFMpOblFY7X8TQs.png', NULL, '2024-01-01 10:00:00');

-- Insert test decks
INSERT INTO decks (id, name, user_id, cards, evolution_slots, average_elixir, created_at, updated_at) VALUES
(1, 'Test Deck 1', 1, '[26000000, 26000001, 26000002, 26000003, 26000004, 26000005, 28000000, 28000001]', '[]', 3.50, '2024-01-01 10:30:00', '2024-01-01 10:30:00'),
(2, 'Test Deck 2', 1, '[26000000, 26000003, 26000004, 26000006, 26000007, 26000005, 28000000, 28000001]', '[26000000, 26000003]', 4.25, '2024-01-01 11:00:00', '2024-01-01 11:00:00'),
(3, 'Test Deck 3', 2, '[26000001, 26000002, 26000005, 26000006, 26000007, 26000004, 28000000, 28000001]', '[26000006]', 4.00, '2024-01-01 12:00:00', '2024-01-01 12:00:00');