# Design Document

## Overview

This design document outlines the implementation of Docker-based database integration for the Clash Royale Deck Builder. The solution provides a containerized MySQL database with automatic schema initialization, environment-specific configuration, and seamless integration with the existing FastAPI backend.

## Architecture

### Container Architecture
```
clash-deck-builder/
├── docker-compose.yml          # Multi-service orchestration
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.prod.yml     # Production overrides
├── .env                        # Local environment variables (gitignored)
├── .env.example                # Environment template for setup
├── .env.local                  # Local testing environment
├── .env.docker                 # Docker-specific environment
├── backend/
│   ├── Dockerfile              # Backend container definition
│   ├── pyproject.toml          # UV project configuration
│   ├── uv.lock                 # UV locked dependencies
│   └── src/                    # Application code
├── database/
│   ├── init/                   # Database initialization scripts
│   │   ├── 01-schema.sql       # Table creation
│   │   ├── 02-indexes.sql      # Performance indexes
│   │   └── 03-seed-data.sql    # Development seed data
│   ├── migrations/             # Schema migration scripts
│   └── backups/                # Database backup storage
└── scripts/
    ├── setup-env.sh            # Environment setup script
    └── deploy.sh               # Deployment script
```

### Service Communication
- **Frontend** (host:3000) → **Backend** (container:8000) → **Database** (container:3306)
- Internal Docker network for backend-database communication
- Host port mapping for external access during development

## Components and Interfaces

### 1. Docker Compose Configuration

#### Main Compose File (docker-compose.yml)
```yaml
version: '3.8'

services:
  database:
    image: mysql:8.0
    container_name: clash-db
    env_file:
      - .env.docker
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    ports:
      - "${DB_PORT:-3306}:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init:/docker-entrypoint-initdb.d
      - ./database/backups:/backups
    networks:
      - clash-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: clash-backend
    env_file:
      - .env.docker
    environment:
      DATABASE_URL: mysql+pymysql://${DB_USER}:${DB_PASSWORD}@database:3306/${DB_NAME}
      CLASH_ROYALE_API_KEY: ${CLASH_ROYALE_API_KEY}
      DEBUG: ${DEBUG:-false}
      LOG_LEVEL: ${LOG_LEVEL:-info}
      CORS_ORIGINS: ${CORS_ORIGINS}
    ports:
      - "8000:8000"
    depends_on:
      database:
        condition: service_healthy
    networks:
      - clash-network
    volumes:
      - ./backend:/app
    command: uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  mysql_data:

networks:
  clash-network:
    driver: bridge
```

#### Development Override (docker-compose.dev.yml)
```yaml
version: '3.8'

services:
  database:
    env_file:
      - .env.local
    volumes:
      - ./database/init/03-seed-data.sql:/docker-entrypoint-initdb.d/03-seed-data.sql

  backend:
    env_file:
      - .env.local
    environment:
      DEBUG: "true"
      LOG_LEVEL: "debug"
    volumes:
      - ./backend/src:/app/src

#### Production Override (docker-compose.prod.yml)
```yaml
version: '3.8'

services:
  database:
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init:/docker-entrypoint-initdb.d:ro
      - ./database/backups:/backups

  backend:
    env_file:
      - .env
    restart: unless-stopped
    environment:
      DEBUG: "false"
      LOG_LEVEL: "warning"
    command: uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Copy uv configuration files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Database Schema Initialization

#### Schema Creation (database/init/01-schema.sql)
```sql
-- Users table for future authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Decks table for storing user decks
CREATE TABLE IF NOT EXISTS decks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INT,
    cards JSON NOT NULL,
    evolution_slots JSON DEFAULT '[]',
    average_elixir DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Cards cache table for storing Clash Royale API data
CREATE TABLE IF NOT EXISTS cards_cache (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    elixir_cost INT NOT NULL,
    rarity VARCHAR(20) NOT NULL,
    type VARCHAR(20) NOT NULL,
    arena VARCHAR(50),
    image_url TEXT NOT NULL,
    image_url_evo TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Performance Indexes (database/init/02-indexes.sql)
```sql
-- Indexes for better query performance
CREATE INDEX idx_decks_user_id ON decks(user_id);
CREATE INDEX idx_decks_name ON decks(name);
CREATE INDEX idx_decks_created_at ON decks(created_at);
CREATE INDEX idx_cards_cache_name ON cards_cache(name);
CREATE INDEX idx_cards_cache_rarity ON cards_cache(rarity);
CREATE INDEX idx_cards_cache_elixir_cost ON cards_cache(elixir_cost);
```

### 4. Environment Configuration

#### Environment Template (.env.example)
```bash
# Database Configuration
DB_ROOT_PASSWORD=your_secure_root_password
DB_NAME=clash_deck_builder
DB_USER=clash_user
DB_PASSWORD=your_secure_user_password
DB_PORT=3306

# Application Configuration
CLASH_ROYALE_API_KEY=your_clash_royale_api_key_here
DEBUG=false
LOG_LEVEL=info

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Deployment Configuration
ENVIRONMENT=production
```

#### Local Testing Environment (.env.local)
```bash
# Database Configuration
DB_ROOT_PASSWORD=rootpassword
DB_NAME=clash_deck_builder_dev
DB_USER=clash_user
DB_PASSWORD=clash_password
DB_PORT=3306

# Application Configuration
CLASH_ROYALE_API_KEY=test_api_key_or_mock
DEBUG=true
LOG_LEVEL=debug

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Local Development
ENVIRONMENT=development
```

#### Docker Environment (.env.docker)
```bash
# Database Configuration
DB_ROOT_PASSWORD=docker_root_password
DB_NAME=clash_deck_builder_docker
DB_USER=clash_user
DB_PASSWORD=docker_user_password
DB_PORT=3306

# Application Configuration
CLASH_ROYALE_API_KEY=${CLASH_ROYALE_API_KEY}
DEBUG=false
LOG_LEVEL=info

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Docker Environment
ENVIRONMENT=docker
```

#### Environment Setup Script (scripts/setup-env.sh)
```bash
#!/bin/bash

# Setup environment files for local development
echo "Setting up environment files..."

# Copy example to local if it doesn't exist
if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo "Created .env.local from template"
fi

# Copy example to docker if it doesn't exist
if [ ! -f .env.docker ]; then
    cp .env.example .env.docker
    echo "Created .env.docker from template"
fi

# Create production .env if it doesn't exist (for deployment)
if [ ! -f .env ] && [ "$1" = "production" ]; then
    cp .env.example .env
    echo "Created .env for production - PLEASE UPDATE WITH REAL VALUES"
    echo "WARNING: Update .env with secure passwords and real API keys!"
fi

echo "Environment setup complete!"
echo "Please update the environment files with your actual values."
```

### 5. Database Connection Management

#### Enhanced Database Utility (backend/src/utils/database.py)
```python
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
from typing import Generator
import logging
from .config import get_settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.settings = get_settings()
        self.pool = None
        self._create_connection_pool()
    
    def _create_connection_pool(self):
        """Create MySQL connection pool"""
        try:
            config = {
                'user': self.settings.db_user,
                'password': self.settings.db_password,
                'host': self.settings.db_host,
                'database': self.settings.db_name,
                'pool_name': 'clash_pool',
                'pool_size': 10,
                'pool_reset_session': True,
                'autocommit': False
            }
            self.pool = pooling.MySQLConnectionPool(**config)
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator:
        """Get database connection from pool"""
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()
```

### 6. Migration System

#### Migration Runner (database/migrations/migrate.py)
```python
import os
import mysql.connector
from pathlib import Path
import logging

class MigrationRunner:
    def __init__(self, connection_config):
        self.config = connection_config
        self.migrations_dir = Path(__file__).parent
    
    def run_migrations(self):
        """Run all pending migrations"""
        with mysql.connector.connect(**self.config) as conn:
            cursor = conn.cursor()
            
            # Create migrations table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Get applied migrations
            cursor.execute("SELECT version FROM schema_migrations")
            applied = {row[0] for row in cursor.fetchall()}
            
            # Run pending migrations
            migration_files = sorted(self.migrations_dir.glob("*.sql"))
            for migration_file in migration_files:
                version = migration_file.stem
                if version not in applied:
                    self._apply_migration(cursor, migration_file, version)
                    conn.commit()
    
    def _apply_migration(self, cursor, migration_file, version):
        """Apply a single migration"""
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        cursor.execute(sql)
        cursor.execute(
            "INSERT INTO schema_migrations (version) VALUES (%s)",
            (version,)
        )
        logging.info(f"Applied migration: {version}")
```

## Data Models

### Enhanced Configuration Model
```python
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database settings
    db_host: str = "database"
    db_port: int = 3306
    db_name: str = "clash_deck_builder"
    db_user: str = "clash_user"
    db_password: str
    db_root_password: str
    
    # Application settings
    clash_royale_api_key: str
    debug: bool = False
    log_level: str = "info"
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000"]
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
```

## Error Handling

### Database-Specific Error Handling
```python
from mysql.connector import Error as MySQLError
from fastapi import HTTPException

class DatabaseErrorHandler:
    @staticmethod
    def handle_mysql_error(error: MySQLError) -> HTTPException:
        if error.errno == 1062:  # Duplicate entry
            return HTTPException(status_code=409, detail="Resource already exists")
        elif error.errno == 1452:  # Foreign key constraint
            return HTTPException(status_code=400, detail="Invalid reference")
        else:
            return HTTPException(status_code=500, detail="Database operation failed")
```

## Testing Strategy

### Integration Testing with Test Containers
```python
import pytest
from testcontainers.mysql import MySqlContainer
from backend.src.utils.database import DatabaseManager

@pytest.fixture(scope="session")
def test_database():
    with MySqlContainer("mysql:8.0") as mysql:
        # Configure test database
        yield mysql.get_connection_url()

@pytest.fixture
def db_manager(test_database):
    return DatabaseManager(test_database)
```

## Performance Considerations

### Connection Pooling
- MySQL connection pool with 10 connections
- Connection reuse and automatic cleanup
- Pool monitoring and health checks

### Database Optimization
- Proper indexing on frequently queried columns
- JSON column optimization for card data
- Query performance monitoring

### Caching Strategy
- Redis integration for frequently accessed data
- Card data caching with TTL
- Query result caching for expensive operations

## Security Considerations

### Container Security
- Non-root user in application container
- Minimal base images with security updates
- Secret management through environment variables

### Database Security
- Separate database user with limited privileges
- Network isolation through Docker networks
- Encrypted connections in production

### Data Protection
- Regular automated backups
- Backup encryption and secure storage
- Data retention policies

## Deployment Strategy

### Environment Management
- **Local Development**: Use `.env.local` for testing with safe default values
- **Docker Development**: Use `.env.docker` for containerized development
- **Production**: Use `.env` with secure, environment-specific values
- **CI/CD**: Inject environment variables through deployment pipeline secrets

### Deployment Script (scripts/deploy.sh)
```bash
#!/bin/bash

ENVIRONMENT=${1:-production}

echo "Deploying to $ENVIRONMENT environment..."

# Validate required environment variables
required_vars=("DB_ROOT_PASSWORD" "DB_PASSWORD" "CLASH_ROYALE_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set"
        exit 1
    fi
done

# Use appropriate compose file
case $ENVIRONMENT in
    "development")
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        ;;
    "production")
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        ;;
    *)
        echo "Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

echo "Deployment to $ENVIRONMENT completed!"
```

### Environment Variable Injection
- **Development**: Load from `.env.local` file
- **Docker**: Load from `.env.docker` file  
- **Production**: Load from `.env` file or system environment variables
- **CI/CD**: Inject through pipeline secrets (GitHub Actions, GitLab CI, etc.)

### Security Best Practices
- Never commit `.env`, `.env.local`, or `.env.docker` files to version control
- Use strong, unique passwords for each environment
- Rotate API keys and database passwords regularly
- Use secrets management in production (AWS Secrets Manager, Azure Key Vault, etc.)