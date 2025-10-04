-- Database initialization: Create users and set permissions
-- This script creates the application user and grants necessary permissions
-- It runs before the schema creation

-- Create the application user if it doesn't exist
-- Note: In MySQL 8.0, we need to create user first, then grant privileges

-- Create user for Docker network access (%)
CREATE USER IF NOT EXISTS 'clash_user'@'%' IDENTIFIED BY 'docker_user_password123';

-- Create user for host machine access (for local development)
-- This allows connections from the Docker host machine
CREATE USER IF NOT EXISTS 'clash_user'@'172.%.%.%' IDENTIFIED BY 'docker_user_password123';
CREATE USER IF NOT EXISTS 'clash_user'@'172.20.0.%' IDENTIFIED BY 'docker_user_password123';
CREATE USER IF NOT EXISTS 'clash_user'@'localhost' IDENTIFIED BY 'docker_user_password123';
CREATE USER IF NOT EXISTS 'clash_user'@'127.0.0.1' IDENTIFIED BY 'docker_user_password123';

-- Grant all privileges on the application database
GRANT ALL PRIVILEGES ON clash_deck_builder_dev.* TO 'clash_user'@'%';
GRANT ALL PRIVILEGES ON clash_deck_builder_dev.* TO 'clash_user'@'172.%.%.%';
GRANT ALL PRIVILEGES ON clash_deck_builder_dev.* TO 'clash_user'@'172.20.0.%';
GRANT ALL PRIVILEGES ON clash_deck_builder_dev.* TO 'clash_user'@'localhost';
GRANT ALL PRIVILEGES ON clash_deck_builder_dev.* TO 'clash_user'@'127.0.0.1';

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;

-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS clash_deck_builder_dev 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Use the database for subsequent scripts
USE clash_deck_builder_dev;