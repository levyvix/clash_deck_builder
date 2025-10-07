# Database Schema

This document describes the database schema for the Clash Royale Deck Builder application.

## Overview

The database uses MySQL 8.0 with the following character set and collation:
- **Character Set**: `utf8mb4`
- **Collation**: `utf8mb4_unicode_ci`

## Tables

### Users
Stores user account information.

```sql
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `google_id` varchar(255) COLLATE utf8mb4_unicode_ci UNIQUE,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `avatar` text COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `last_login` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_users_email` (`email`),
  KEY `idx_users_google_id` (`google_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Decks
Stores user-created decks.

```sql
CREATE TABLE `decks` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cards` json NOT NULL,
  `evolutions` json DEFAULT NULL,
  `average_elixir` decimal(3,1) NOT NULL,
  `is_public` tinyint(1) NOT NULL DEFAULT '0',
  `view_count` int NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_decks_user_id` (`user_id`),
  KEY `idx_decks_public` (`is_public`, `view_count`),
  CONSTRAINT `fk_decks_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Cards
Stores card metadata and statistics.

```sql
CREATE TABLE `cards` (
  `id` int NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rarity` enum('Common','Rare','Epic','Legendary','Champion') COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` enum('Troop','Spell','Building') COLLATE utf8mb4_unicode_ci NOT NULL,
  `elixir` tinyint NOT NULL,
  `arena` tinyint NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `icon_urls` json DEFAULT NULL,
  `has_evolution` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cards_rarity` (`rarity`),
  KEY `idx_cards_type` (`type`),
  KEY `idx_cards_elixir` (`elixir`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### User_Cards
Tracks user's card collection and levels.

```sql
CREATE TABLE `user_cards` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `card_id` int NOT NULL,
  `level` tinyint NOT NULL DEFAULT '1',
  `count` int NOT NULL DEFAULT '0',
  `is_favorite` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_user_card` (`user_id`, `card_id`),
  KEY `idx_user_favorites` (`user_id`, `is_favorite`),
  CONSTRAINT `fk_user_cards_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_cards_card` FOREIGN KEY (`card_id`) REFERENCES `cards` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Deck_Stats
Tracks deck performance and usage statistics.

```sql
CREATE TABLE `deck_stats` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `deck_id` bigint NOT NULL,
  `wins` int NOT NULL DEFAULT '0',
  `losses` int NOT NULL DEFAULT '0',
  `last_played` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_deck_stats_deck` (`deck_id`),
  KEY `idx_deck_stats_performance` (`wins`, `losses`),
  CONSTRAINT `fk_deck_stats_deck` FOREIGN KEY (`deck_id`) REFERENCES `decks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Indexing Strategy

### Primary Keys
- All tables use auto-incrementing BIGINT primary keys
- UUIDs are not used to maintain index efficiency

### Foreign Keys
- All foreign keys are indexed
- ON DELETE CASCADE is used where appropriate

### Composite Indexes
- Created for commonly filtered columns
- Order of columns in composite indexes follows query patterns

### Full-Text Search
- Enabled on card names and descriptions
- Used for search functionality

## Data Types

### Integer Types
- `TINYINT`: Boolean flags and small ranges (0-255)
- `INT`: Standard integers
- `BIGINT`: Primary and foreign keys

### String Types
- `VARCHAR`: Variable-length strings with length limits
- `TEXT`: For longer text content
- `ENUM`: For fixed sets of values

### JSON
- Used for flexible schema data
- Indexed using generated columns where needed

## Relationships

### Users to Decks (One-to-Many)
- A user can have multiple decks
- Decks are deleted when a user is deleted

### Users to Cards (Many-to-Many)
- Users can collect multiple cards
- Cards can be collected by multiple users
- Junction table tracks additional metadata (level, count, etc.)

### Decks to Cards (Many-to-Many)
- A deck contains multiple cards
- A card can be in multiple decks
- Stored as JSON array in the decks table for performance

## Performance Considerations

### Read Optimization
- Frequently accessed data is denormalized where appropriate
- Materialized views for complex queries
- Appropriate indexing strategy

### Write Optimization
- Batch operations where possible
- Delayed writes for non-critical updates
- Background processing for expensive operations

## Data Retention

### Active Data
- User accounts: Kept indefinitely unless deleted
- Decks: Kept until user deletes them
- Card collection: Kept with user account

### Audit Data
- Login attempts: 90 days
- API access logs: 30 days
- Error logs: 30 days

## Backup Strategy

### Automated Backups
- Full database backup daily
- Incremental backups every 6 hours
- Transaction logs backed up every 15 minutes

### Retention
- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: 12 months

## Security

### Data Encryption
- Data at rest: AES-256 encryption
- Data in transit: TLS 1.3
- Sensitive fields encrypted in database

### Access Control
- Principle of least privilege
- Separate database users for different services
- IP whitelisting for database access

## Migration Strategy

### Versioning
- Schema versions tracked in `schema_migrations` table
- Each migration is idempotent
- Backward compatibility maintained for at least one version

### Rollback
- Each migration includes rollback steps
- Tested in staging before production
- Point-in-time recovery available

## Monitoring

### Performance Metrics
- Query performance
- Connection pool usage
- Replication lag

### Alerting
- Slow queries (> 1s)
- Connection pool exhaustion
- Replication issues

## Maintenance

### Routine Maintenance
- Weekly optimization of tables
- Monthly index reorganization
- Quarterly statistics update

### Vacuuming
- Automated vacuuming of dead tuples
- Manual vacuuming after large data operations

## Best Practices

### Naming Conventions
- Tables: plural nouns (`users`, `decks`)
- Columns: snake_case
- Foreign Keys: `fk_[table]_[column]`
- Indexes: `idx_[table]_[columns]`

### Constraints
- NOT NULL where appropriate
- DEFAULT values for common cases
- CHECK constraints for data validation

### Documentation
- All tables and columns have comments
- Complex queries documented
- Known issues and workarounds documented
