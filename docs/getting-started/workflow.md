# Development Workflow

Learn the recommended workflow for developing features and contributing to the Clash Royale Deck Builder.

## Daily Development Session

### 1. Start Services

Using Docker (recommended):
```bash
# Start all services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

Or run services individually:
```bash
# Terminal 1: Database
docker-compose up -d database

# Terminal 2: Backend
cd backend
uv run uvicorn src.main:app --reload

# Terminal 3: Frontend
cd frontend
npm start
```

### 2. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: `localhost:3306`

### 3. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Branch Strategy

### Main Branch

- **`main`** - Main development and production branch

### Creating Feature Branches

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Example
git checkout -b feature/add-deck-sharing
git checkout -b fix/evolution-card-bug
git checkout -b refactor/improve-card-service
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test improvements
- `chore/` - Maintenance tasks

## Making Changes

### 1. Backend Changes

```bash
cd backend

# Make your changes to code

# Run linters
uv run black .
uv run flake8 .

# Run tests
uv run pytest

# Run specific tests
uv run pytest tests/unit/test_card_service.py

# Check test coverage
uv run pytest --cov=src --cov-report=html
```

### 2. Frontend Changes

```bash
cd frontend

# Make your changes to code

# Run tests
npm test

# Run tests once (non-interactive)
npm run test:run

# Check for TypeScript errors
npm run build

# Run linter (if configured)
npm run lint
```

### 3. Database Changes

For schema changes:

```bash
# Create migration file
cd database/migrations

# Create new migration (format: YYYYMMDD_HHMMSS_description.sql)
touch 20240101_120000_add_deck_sharing.sql
touch 20240101_120000_add_deck_sharing.rollback.sql

# Write SQL migration
nano 20240101_120000_add_deck_sharing.sql

# Run migration
python migrate.py

# Test rollback
python migrate.py --rollback 20240101_120000_add_deck_sharing
```

See [Database Migrations](../operations/migrations.md) for details.

## Testing Your Changes

### Unit Tests

Test individual functions and methods:

```bash
# Backend
cd backend
uv run pytest tests/unit/

# Frontend
cd frontend
npm test -- --testPathPattern=unit
```

### Integration Tests

Test component interactions:

```bash
# Backend (requires database)
cd backend
uv run pytest tests/integration/

# Frontend
cd frontend
npm test -- --testPathPattern=integration
```

### Contract Tests

Verify API contracts:

```bash
cd backend
uv run pytest tests/contract/
```

### End-to-End Tests

Test full user workflows (if configured):

```bash
npm run test:e2e
```

## Committing Changes

### Commit Message Format

Use conventional commits:

```bash
# Format
<type>(<scope>): <subject>

# Examples
git commit -m "feat(deck): add deck sharing functionality"
git commit -m "fix(evolution): resolve evolution card slot validation"
git commit -m "refactor(api): improve error handling in card service"
git commit -m "docs: update API documentation for deck endpoints"
git commit -m "test: add unit tests for deck service"
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring
- `docs` - Documentation
- `test` - Tests
- `style` - Formatting
- `chore` - Maintenance

### Commit Best Practices

```bash
# Stage specific files
git add backend/src/api/decks.py
git add frontend/src/components/DeckSharing.tsx

# Review changes before committing
git diff --staged

# Commit with descriptive message
git commit -m "feat(deck): add deck sharing functionality"

# Push to your feature branch
git push origin feature/your-feature-name
```

## Creating Pull Requests

### 1. Prepare Your Branch

```bash
# Ensure all tests pass
cd backend && uv run pytest
cd frontend && npm test

# Update from main branch
git checkout main
git pull origin main
git checkout feature/your-feature-name
git merge main

# Resolve any conflicts
git mergetool
```

### 2. Push Changes

```bash
git push origin feature/your-feature-name
```

### 3. Create PR

On GitHub/GitLab:
1. Navigate to the repository
2. Click "New Pull Request"
3. **Base branch**: `main`
4. **Compare branch**: `feature/your-feature-name`
5. Fill in PR template:
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (if UI changes)

### PR Checklist

- [ ] All tests passing
- [ ] Code linted and formatted
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Meaningful commit messages
- [ ] PR description complete

## Code Review Process

### As an Author

- Respond to feedback promptly
- Make requested changes
- Re-request review after updates
- Keep PRs focused and small

### As a Reviewer

- Be constructive and specific
- Test the changes locally
- Check for:
  - Code quality
  - Test coverage
  - Documentation
  - Security issues
  - Performance implications

## Common Development Tasks

### Adding a Backend Endpoint

1. **Create route handler** in `src/api/[module].py`
2. **Implement business logic** in `src/services/[module]_service.py`
3. **Add data model** (if needed) in `src/models/`
4. **Write tests** in `tests/unit/` and `tests/contract/`
5. **Update documentation** (docstrings for auto-generated docs)

See [Backend Development](../development/backend.md#adding-endpoints) for details.

### Adding a Frontend Component

1. **Create component** in `src/components/[Component].tsx`
2. **Create styles** in `src/styles/[Component].css`
3. **Add service functions** in `src/services/` (if API calls needed)
4. **Write tests** in `src/components/[Component].test.tsx`
5. **Import and use** in parent components

See [Frontend Development](../development/frontend.md#adding-components) for details.

### Updating Dependencies

**Backend:**
```bash
cd backend

# Add new dependency
uv add package-name

# Update dependencies
uv lock --upgrade

# Sync with lock file
uv sync
```

**Frontend:**
```bash
cd frontend

# Add new dependency
npm install package-name

# Update dependencies
npm update

# Audit for vulnerabilities
npm audit
npm audit fix
```

## Debugging

### Backend Debugging

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=debug

# Run with verbose logging
cd backend
uv run uvicorn src.main:app --reload --log-level debug

# View logs
docker-compose logs -f backend

# Interactive debugging with pdb
# Add to code: import pdb; pdb.set_trace()
```

### Frontend Debugging

```bash
# Enable source maps
GENERATE_SOURCEMAP=true npm start

# Use React DevTools (browser extension)
# Use Chrome/Firefox DevTools

# View console logs
console.log('Debug info:', variable)
```

### Database Debugging

```bash
# Connect to database
docker-compose exec database mysql -u clash_user -p clash_deck_builder

# View query logs (add to docker-compose.yml):
# command: --general-log=1 --general-log-file=/var/log/mysql/general.log

# Check slow queries
SHOW FULL PROCESSLIST;
```

## Next Steps

- Learn about [Backend Development](../development/backend.md)
- Explore [Frontend Development](../development/frontend.md)
- Understand [Testing Strategies](../development/testing.md)
- Review [API Reference](../api/overview.md)
