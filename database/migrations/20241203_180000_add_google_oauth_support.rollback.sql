-- Rollback: Remove Google OAuth support from users table
-- This rollback script reverts the Google OAuth changes to the users table

-- Drop Google OAuth specific indexes
DROP INDEX idx_users_google_id ON users;
DROP INDEX idx_users_email ON users;

-- Drop Google OAuth specific constraints
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_google_id_not_empty;
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_name_length;
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_email_format;

-- Remove Google OAuth columns
ALTER TABLE users 
DROP COLUMN IF EXISTS google_id,
DROP COLUMN IF EXISTS name,
DROP COLUMN IF EXISTS avatar;

-- Restore original column constraints
ALTER TABLE users 
MODIFY COLUMN username VARCHAR(50) UNIQUE NOT NULL,
MODIFY COLUMN email VARCHAR(100) UNIQUE NOT NULL;

-- Restore original constraints
ALTER TABLE users 
ADD CONSTRAINT chk_username_length CHECK (CHAR_LENGTH(username) >= 3),
ADD CONSTRAINT chk_email_format CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$');

-- Restore original table comment
ALTER TABLE users COMMENT = 'User accounts for deck ownership and future authentication';