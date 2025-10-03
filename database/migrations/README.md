# Database Migration System

This directory contains the database migration framework for the Clash Royale Deck Builder application.

## Overview

The migration system provides:
- **Schema versioning**: Track and apply database schema changes
- **Rollback support**: Undo migrations when needed
- **Automated execution**: Run migrations during container startup
- **Migration tracking**: Keep history of applied migrations
- **Checksum validation**: Ensure migration integrity

## File Structure

```
database/migrations/
├── migrate.py              # Core migration runner framework
├── run_migrations.py       # Integration with backend config
├── __init__.py            # Package initialization
├── README.md              # This documentation
├── YYYYMMDD_HHMMSS_*.sql  # Migration files
└── *.rollback.sql         # Rollback scripts (optional)
```

## Migration File Naming Convention

Migration files must follow this naming pattern:
```
YYYYMMDD_HHMMSS_description.sql
```

Examples:
- `20241203_120000_add_user_preferences_table.sql`
- `20241203_130000_create_deck_sharing_indexes.sql`
- `20241204_090000_update_card_cache_schema.sql`

## Creating Migrations

### 1. Create Migration File

Create a new migration file with the proper naming convention:

```sql
-- 20241203_140000_add_user_settings_table.sql

CREATE TABLE user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_setting (user_id, setting_key)
);

CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX idx_user_settings_key ON user_settings(setting_key);
```

### 2. Create Rollback Script (Optional)

Create a corresponding rollback script:

```sql
-- 20241203_140000_add_user_settings_table.rollback.sql

DROP TABLE IF EXISTS user_settings;
```

## Running Migrations

### Using Backend Configuration

The easiest way to run migrations is using the integrated script:

```bash
# Run all pending migrations
python database/migrations/run_migrations.py migrate

# Check migration status
python database/migrations/run_migrations.py status
```

### Using Direct Migration Runner

For more control, use the migration runner directly:

```bash
# Run migrations
python database/migrations/migrate.py migrate \
  --host localhost \
  --port 3306 \
  --user clash_user \
  --password your_password \
  --database clash_deck_builder

# Check status
python database/migrations/migrate.py status \
  --host localhost \
  --port 3306 \
  --user clash_user \
  --password your_password \
  --database clash_deck_builder

# Rollback to specific version
python database/migrations/migrate.py rollback \
  --target 20241203_120000 \
  --host localhost \
  --port 3306 \
  --user clash_user \
  --password your_password \
  --database clash_deck_builder
```

### Environment Variables

The migration runner supports these environment variables:

- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 3306)
- `DB_USER` - Database user (default: root)
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name (default: clash_deck_builder)

## Docker Integration

Migrations are automatically executed during container startup. See the Docker integration section for details.

## Migration Tracking

The system creates a `schema_migrations` table to track applied migrations:

```sql
CREATE TABLE schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64),
    execution_time_ms INT DEFAULT 0
);
```

## Best Practices

### 1. Migration Content
- **Idempotent operations**: Use `IF NOT EXISTS`, `IF EXISTS` where appropriate
- **Backward compatible**: Avoid breaking changes when possible
- **Small changes**: Keep migrations focused and atomic
- **Test thoroughly**: Test migrations on development data first

### 2. Rollback Scripts
- **Always create rollbacks**: For any destructive changes
- **Test rollbacks**: Ensure rollback scripts work correctly
- **Data preservation**: Consider data migration in rollbacks

### 3. Naming and Organization
- **Descriptive names**: Use clear, descriptive migration names
- **Chronological order**: Use timestamp-based versioning
- **Team coordination**: Coordinate migration creation in teams

## Examples

### Adding a New Table

```sql
-- 20241203_150000_create_deck_templates_table.sql

CREATE TABLE IF NOT EXISTS deck_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cards JSON NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    is_public BOOLEAN DEFAULT FALSE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_deck_templates_category ON deck_templates(category);
CREATE INDEX idx_deck_templates_public ON deck_templates(is_public);
CREATE INDEX idx_deck_templates_created_by ON deck_templates(created_by);
```

### Adding a Column

```sql
-- 20241203_160000_add_deck_favorite_flag.sql

ALTER TABLE decks 
ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_decks_favorite ON decks(is_favorite);
```

### Data Migration

```sql
-- 20241203_170000_migrate_legacy_deck_data.sql

-- Update existing decks with default evolution slots if empty
UPDATE decks 
SET evolution_slots = '[]' 
WHERE evolution_slots IS NULL OR evolution_slots = '';

-- Recalculate average elixir for existing decks
UPDATE decks 
SET average_elixir = (
    SELECT AVG(JSON_EXTRACT(card.value, '$.elixir_cost'))
    FROM JSON_TABLE(cards, '$[*]' COLUMNS (
        card_id INT PATH '$.id',
        elixir_cost INT PATH '$.elixir_cost'
    )) AS card
) 
WHERE average_elixir = 0.00;
```

## Troubleshooting

### Common Issues

1. **Migration fails with syntax error**
   - Check SQL syntax in migration file
   - Ensure proper semicolon separation
   - Validate against MySQL version

2. **Migration already applied error**
   - Check `schema_migrations` table
   - Verify migration version numbering
   - Use `status` command to see applied migrations

3. **Rollback script not found**
   - Ensure rollback script exists with correct naming
   - Check file permissions
   - Verify rollback script syntax

### Recovery

If migrations fail or database gets into inconsistent state:

1. **Check migration status**:
   ```bash
   python database/migrations/run_migrations.py status
   ```

2. **Manual rollback**:
   ```bash
   # Rollback to last known good version
   python database/migrations/migrate.py rollback --target YYYYMMDD_HHMMSS
   ```

3. **Manual cleanup**:
   ```sql
   -- Remove failed migration from tracking table
   DELETE FROM schema_migrations WHERE version = 'YYYYMMDD_HHMMSS';
   ```

4. **Re-run migrations**:
   ```bash
   python database/migrations/run_migrations.py migrate
   ```

## Integration with Application

The migration system integrates with the main application through:

1. **Startup migrations**: Automatic execution during container startup
2. **Configuration sharing**: Uses same database config as main app
3. **Logging integration**: Consistent logging with application
4. **Error handling**: Proper error reporting and recovery