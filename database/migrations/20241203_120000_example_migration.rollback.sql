-- Rollback script for example migration
-- This demonstrates rollback functionality

-- Remove the test user
DELETE FROM users WHERE username = 'migration_test';

-- Drop the index
DROP INDEX idx_users_last_login ON users;

-- Remove the column
ALTER TABLE users DROP COLUMN last_login;