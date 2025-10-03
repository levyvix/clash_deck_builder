-- Migration: Add Google OAuth support to users table
-- This migration updates the users table to support Google OAuth authentication
-- Since we can nuke existing data, we'll clear everything and recreate the schema

-- Drop foreign key constraint first to allow truncation
ALTER TABLE decks DROP FOREIGN KEY decks_ibfk_1;

-- Clear existing data
TRUNCATE TABLE decks;
TRUNCATE TABLE users;

-- Recreate users table structure for Google OAuth
DROP TABLE users;
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_google_id_not_empty CHECK (CHAR_LENGTH(google_id) > 0),
    CONSTRAINT chk_name_length CHECK (CHAR_LENGTH(name) >= 1 AND CHAR_LENGTH(name) <= 100),
    CONSTRAINT chk_email_format CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create indexes for performance
CREATE UNIQUE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);

-- Update decks table to use VARCHAR for user_id to match users.id
ALTER TABLE decks MODIFY COLUMN user_id VARCHAR(36);

-- Ensure foreign key constraint exists
ALTER TABLE decks ADD CONSTRAINT decks_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Update table comments
ALTER TABLE users COMMENT = 'User accounts with Google OAuth authentication for deck ownership and profile management';