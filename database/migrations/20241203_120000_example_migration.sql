-- Example migration file
-- This demonstrates the migration file format
-- Filename format: YYYYMMDD_HHMMSS_description.sql

-- Add a sample column to demonstrate migration functionality
-- This is just an example and can be removed in production

ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL DEFAULT NULL;

-- Add index for performance
CREATE INDEX idx_users_last_login ON users(last_login);

-- Insert a comment to track this migration
INSERT INTO users (username, email) VALUES 
('migration_test', 'migration@example.com') 
ON DUPLICATE KEY UPDATE username = username;