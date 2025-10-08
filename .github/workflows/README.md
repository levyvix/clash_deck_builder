# GitHub Actions CI/CD Workflows

## Backend CI Pipeline

**File**: `backend-ci.yml`

### Purpose
Automated testing of core backend functionality on every push or pull request to `main` or `develop` branches.

### What It Tests
1. **Unit Tests** - Business logic in services, utilities, and models
2. **Contract Tests** - API endpoint contracts and response formats

**Note**: Integration tests are NOT run in CI because they require a full Docker environment with database. Run integration tests locally with `docker-compose -f docker-compose.test.yml up -d`

### Triggers
- Push to `main` or `develop` branches (only when backend files change)
- Pull requests to `main` or `develop` branches (only when backend files change)

### Infrastructure
- **Python**: 3.11
- **Package Manager**: UV (not pip)
- **Test Framework**: pytest
- **Database**: Not required (unit and contract tests use mocks)

### Workflow Steps
1. Checkout code
2. Set up Python 3.11
3. Install UV package manager
4. Install Python dependencies with `uv sync`
5. Run unit tests
6. Run contract tests
7. Generate JUnit XML test report
8. Upload test results as artifacts

### Required GitHub Secrets

No secrets are required for this workflow. Card data is ingested from JSON files, not the Clash Royale API.

### Viewing Results

1. **GitHub Actions Tab**: See workflow runs and detailed logs
2. **Test Artifacts**: Download JUnit XML reports (retained for 30 days)
3. **PR Checks**: Status checks appear on pull requests

### Running the Same Tests Locally

```bash
cd backend

# Run unit tests (no database needed)
uv run pytest tests/unit/ -v

# Run contract tests (no database needed)
uv run pytest tests/contract/ -v

# Run integration tests (requires Docker database)
docker-compose -f ../docker-compose.test.yml up -d
uv run pytest tests/integration/ -v
```

### Performance

- **Typical run time**: 1-2 minutes
- **Path filtering**: Only runs when backend code changes
- **Fast execution**: No database setup needed for unit/contract tests

### Troubleshooting

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
