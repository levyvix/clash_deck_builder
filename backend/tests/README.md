# Integration Testing Setup

This directory contains comprehensive integration tests for the Clash Royale Deck Builder's database operations and Docker environment.

## Overview

The integration tests verify:
- Database connection and health checks
- CRUD operations for decks, users, and cards
- Database migration system
- Backup and restore functionality
- Docker environment integration
- Transaction handling and error recovery

## Test Structure

```
tests/
├── integration/                    # Integration tests
│   ├── test_database_connection.py # Database connectivity tests
│   ├── test_deck_operations.py     # Deck CRUD operation tests
│   ├── test_migration_system.py    # Migration system tests
│   ├── test_backup_restore.py      # Backup/restore functionality tests
│   └── test_docker_environment.py  # Docker environment tests
├── fixtures/                       # Test fixtures and utilities
│   ├── test_db_manager.py          # Test database management
│   └── test_data.sql               # Test seed data
├── conftest.py                     # Pytest configuration and fixtures
├── run_integration_tests.py        # Test runner script
└── README.md                       # This file
```

## Prerequisites

1. **Docker and Docker Compose**: Required for running test database containers
2. **Python 3.11+**: Backend runtime
3. **UV Package Manager**: For dependency management
4. **MySQL Client Tools** (optional): For manual database operations

## Quick Start

### Option 1: Using Test Scripts (Recommended)

**Linux/macOS:**
```bash
# Make script executable
chmod +x scripts/test-setup.sh

# Run tests
./scripts/test-setup.sh
```

**Windows PowerShell:**
```powershell
# Run tests
.\scripts\test-setup.ps1
```

### Option 2: Using Python Test Runner

```bash
# From project root
cd backend
python tests/run_integration_tests.py
```

### Option 3: Manual Setup

```bash
# 1. Start test database
docker-compose -f docker-compose.test.yml up -d test-database

# 2. Wait for database to be ready (check logs)
docker-compose -f docker-compose.test.yml logs -f test-database

# 3. Run tests
cd backend
uv run pytest tests/integration/ -v
```

## Test Configuration

### Test Database

The tests use an isolated MySQL database container with the following configuration:

- **Host**: localhost
- **Port**: 3307 (to avoid conflicts with main database)
- **Database**: clash_deck_builder_test
- **User**: test_user
- **Password**: test_password

### Environment Variables

Test environment variables are automatically set by the test fixtures:

```bash
TESTING=true
DATABASE_URL=mysql+pymysql://test_user:test_password@localhost:3307/clash_deck_builder_test
DB_HOST=localhost
DB_PORT=3307
DB_NAME=clash_deck_builder_test
DB_USER=test_user
DB_PASSWORD=test_password
DEBUG=true
LOG_LEVEL=debug
```

## Test Categories

### 1. Database Connection Tests (`test_database_connection.py`)

- Database manager initialization
- Connection pooling behavior
- Health check functionality
- Schema validation
- Foreign key constraints
- Index verification
- Transaction rollback

### 2. Deck Operations Tests (`test_deck_operations.py`)

- Create, read, update, delete operations
- User isolation and security
- Deck limit enforcement
- JSON serialization/deserialization
- Average elixir calculation
- Error handling

### 3. Migration System Tests (`test_migration_system.py`)

- Schema initialization
- Migration execution
- Rollback functionality
- Data integrity
- Seed data loading

### 4. Backup/Restore Tests (`test_backup_restore.py`)

- Backup creation and validation
- Data integrity preservation
- Foreign key relationship preservation
- JSON data preservation
- Timestamp preservation
- Script availability

### 5. Docker Environment Tests (`test_docker_environment.py`)

- Container health checks
- Network connectivity
- Volume persistence
- Environment isolation
- Resource limits
- Cleanup procedures

## Test Data

### Fixtures

The tests use predefined test data located in `fixtures/test_data.sql`:

- **3 test users** with different IDs and email addresses
- **10 test cards** covering different rarities and types
- **3 test decks** with various configurations

### Data Management

- **Setup**: Each test session starts with a clean database and fresh test data
- **Isolation**: Each test function gets a clean database state
- **Cleanup**: Test data is automatically cleaned up after each test

## Running Specific Tests

### Run all integration tests:
```bash
uv run pytest tests/integration/ -v
```

### Run specific test file:
```bash
uv run pytest tests/integration/test_deck_operations.py -v
```

### Run specific test function:
```bash
uv run pytest tests/integration/test_deck_operations.py::TestDeckOperations::test_create_deck -v
```

### Run tests with coverage:
```bash
uv run pytest tests/integration/ --cov=src --cov-report=html
```

## Troubleshooting

### Common Issues

1. **Docker not running**
   ```
   Error: Docker is not running
   ```
   **Solution**: Start Docker Desktop or Docker daemon

2. **Port conflicts**
   ```
   Error: Port 3307 already in use
   ```
   **Solution**: Stop other services using port 3307 or change test port

3. **Database connection timeout**
   ```
   Error: Test database not ready after 60 seconds
   ```
   **Solution**: Check Docker logs and ensure sufficient resources

4. **Permission errors**
   ```
   Error: Permission denied
   ```
   **Solution**: Ensure Docker has proper permissions and scripts are executable

### Debug Commands

```bash
# Check test database status
docker-compose -f docker-compose.test.yml ps

# View test database logs
docker-compose -f docker-compose.test.yml logs test-database

# Connect to test database manually
mysql -h localhost -P 3307 -u test_user -ptest_password clash_deck_builder_test

# Clean up test environment
docker-compose -f docker-compose.test.yml down -v
```

### Performance Considerations

- **Test Database**: Uses tmpfs for faster I/O operations
- **Connection Pooling**: Limited to 50 connections for test environment
- **Memory**: Configured with reduced buffer sizes for testing
- **Parallel Tests**: Tests can be run in parallel with `-n auto` flag

## CI/CD Integration

The integration tests are designed to work in CI/CD environments:

```yaml
# Example GitHub Actions step
- name: Run Integration Tests
  run: |
    chmod +x scripts/test-setup.sh
    ./scripts/test-setup.sh
```

## Contributing

When adding new integration tests:

1. **Follow naming conventions**: `test_*.py` files, `test_*` functions
2. **Use fixtures**: Leverage existing fixtures for database setup
3. **Clean up**: Ensure tests don't leave persistent state
4. **Document**: Add docstrings explaining test purpose
5. **Isolate**: Tests should be independent and runnable in any order

## Security Notes

- Test database uses non-production credentials
- Test environment is isolated from production data
- Sensitive data should use placeholder values
- Test containers are automatically cleaned up