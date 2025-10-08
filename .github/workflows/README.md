# GitHub Actions CI/CD Workflows

## Backend CI Pipeline

**File**: `backend-ci.yml`

### Purpose
Automated testing of core backend functionality on every push or pull request to `main` or `develop` branches.

### What It Tests
1. **Unit Tests** - Business logic in services, utilities, and models
2. **Contract Tests** - API endpoint contracts and response formats
3. **Core Integration Tests**:
   - Database connection and operations
   - Card database functionality
   - Deck CRUD operations

### Triggers
- Push to `main` or `develop` branches (only when backend files change)
- Pull requests to `main` or `develop` branches (only when backend files change)

### Infrastructure
- **Python**: 3.11
- **Package Manager**: UV (not pip)
- **Database**: MySQL 8.0 service container
- **Test Framework**: pytest

### Workflow Steps
1. Checkout code
2. Set up Python 3.11
3. Install UV package manager
4. Install Python dependencies with `uv sync`
5. Wait for MySQL service to be healthy
6. Set up test database schema
7. Run unit tests
8. Run contract tests
9. Run core integration tests
10. Generate JUnit XML test report
11. Upload test results as artifacts

### Required GitHub Secrets

No secrets are required for this workflow. Card data is ingested from JSON files, not the Clash Royale API.

### Test Database Configuration

The workflow automatically creates a MySQL test database with:
- Database: `clash_deck_builder_test`
- User: `clash_user`
- Password: `test_password`
- Root Password: `root_password`

### Viewing Results

1. **GitHub Actions Tab**: See workflow runs and detailed logs
2. **Test Artifacts**: Download JUnit XML reports (retained for 30 days)
3. **PR Checks**: Status checks appear on pull requests

### Running the Same Tests Locally

```bash
# Start test database
docker-compose -f docker-compose.test.yml up -d

# Run unit tests
cd backend
uv run pytest tests/unit/ -v

# Run contract tests
uv run pytest tests/contract/ -v

# Run core integration tests
uv run pytest tests/integration/test_database_connection.py -v
uv run pytest tests/integration/test_card_database.py -v
uv run pytest tests/integration/test_deck_operations.py -v
```

### Performance

- **Typical run time**: 3-5 minutes
- **Path filtering**: Only runs when backend code changes
- **MySQL health checks**: Ensures database is ready before tests run

### Troubleshooting

**MySQL connection failures**:
- The workflow waits up to 60 seconds for MySQL to be ready
- Check the "Wait for MySQL" step logs

**Dependency installation issues**:
- Verify `pyproject.toml` is valid
- Check UV installation logs

**Test failures**:
- Review detailed logs in the GitHub Actions tab
- Download test-results.xml artifact for detailed failure info
- Run tests locally to reproduce

### Future Enhancements

Consider adding:
- Code coverage reporting (e.g., Codecov)
- Linting and code formatting checks (black, flake8)
- Security scanning (bandit, safety)
- Docker image building and publishing
- Deployment to staging environment
