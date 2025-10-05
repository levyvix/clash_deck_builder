# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clash Royale Deck Builder - A web application for building and managing Clash Royale decks with card filtering, deck persistence, and Google OAuth authentication.

**Core Business Rules:**
- Maximum 20 saved decks per user
- Decks support up to 2 evolution card slots
- Real-time average elixir calculation
- All deck data persists in MySQL database

## Technology Stack

### Backend
- **Python 3.11+** with **UV package manager** (not pip/poetry)
- **FastAPI** with Uvicorn ASGI server on port 8000
- **MySQL 8.0** with mysql-connector-python (not SQLAlchemy)
- **httpx** for external API calls
- **pytest** with pytest-asyncio for testing

### Frontend
- **React 19.2+** with Create React App
- **TypeScript** in strict mode
- **React Router DOM** for routing
- **Jest + React Testing Library** for testing
- Development server on port 3000

### External Integrations
- Clash Royale API for card data
- Google OAuth for user authentication

## Development Commands

### Backend Development
```bash
cd backend
uv run uvicorn src.main:app --reload # Start dev server
uv run pytest                        # Run all tests
uv run pytest tests/unit            # Run unit tests only
uv run pytest tests/integration     # Run integration tests only
uv run black . && uv run flake8 .   # Format and lint
```

### Frontend Development
```bash
cd frontend
npm install                  # Install dependencies
npm start                    # Start dev server (port 3000)
npm run start:local         # Start with .env.local config
npm run start:docker        # Start with .env.docker config
npm test                     # Run tests in watch mode
npm run test:run            # Run tests once
npm run build               # Production build
```

### Docker Development
```bash
# Start full environment (recommended)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start only database
docker-compose up -d database

# View logs
docker-compose logs -f backend
docker-compose logs -f database

# Stop all services
docker-compose down

# Clean up (including volumes)
docker-compose down -v

# Check service status
docker-compose ps
```

### Database Operations
```bash
# Run migrations (migrations are standalone, not part of backend package)
cd database/migrations
python migrate.py

# Ingest card data from Clash Royale API
cd backend
uv run src/scripts/ingest_cards.py

# Connect to database
docker-compose exec database mysql -u clash_user -p clash_deck_builder

# Manual database access
docker-compose exec database mysql -u root -p  # Root access
docker-compose exec database mysql -u clash_user -p clash_deck_builder  # User access
```

## Architecture

### Backend Structure (`backend/src/`)
```
api/          # FastAPI route handlers
├── auth.py       # Authentication endpoints
├── profile.py    # User profile endpoints
├── cards.py      # Card data endpoints
└── decks.py      # Deck management endpoints

models/       # Database models and schema
├── user.py       # User model
├── card.py       # Card model
├── deck.py       # Deck model
└── schema.sql    # Database schema

services/     # Business logic layer
├── auth_service.py        # Authentication logic
├── user_service.py        # User management
├── card_service.py        # Card data processing
├── deck_service.py        # Deck operations
├── clash_api_service.py   # Clash Royale API integration
└── migration_service.py   # Database migrations

middleware/   # Request processing
└── auth_middleware.py     # JWT authentication

utils/        # Configuration and utilities
├── config.py         # Pydantic settings (loads from env files)
├── database.py       # Database connection pooling
└── dependencies.py   # FastAPI dependencies
```

**Key Backend Principles:**
- Layered architecture: API → Services → Models
- Use FastAPI dependency injection via `dependencies.py`
- Separate HTTP handling from business logic
- Configuration via `src/utils/config.py` (Pydantic Settings)
- Database connections use `db_manager` from `utils/database.py`

### Frontend Structure (`frontend/src/`)
```
components/       # React components
├── DeckBuilder.tsx        # Main deck building interface
├── CardGallery.tsx        # Card selection gallery
├── SavedDecks.tsx         # Deck management
├── ProfileSection.tsx     # User profile
├── GoogleSignInButton.tsx # OAuth login
└── [other components]

contexts/         # React context providers
├── AuthContext.tsx        # Authentication state
└── OnboardingContext.tsx  # Onboarding flow

services/         # API and business logic
├── api.ts                 # Backend API client
├── authService.ts         # Authentication logic
├── deckStorageService.ts  # Deck persistence
├── localStorageService.ts # Anonymous deck storage
├── evolutionService.ts    # Evolution card handling
└── errorHandlingService.ts # Error handling

styles/           # Component-specific CSS
└── [component].css
```

**Key Frontend Principles:**
- Component-based architecture with TypeScript
- Service layer for API calls and business logic
- Context providers for global state (Auth, Onboarding)
- API base URL from `config.ts` (reads `REACT_APP_API_BASE_URL`)

## Environment Configuration

### Critical Configuration Files
- **`.env.docker`** - Docker environment variables (used by docker-compose)
- **`backend/src/utils/config.py`** - Backend configuration (Pydantic Settings)
- **`frontend/src/config.ts`** - Frontend configuration (reads `REACT_APP_API_BASE_URL`)

### Required Environment Variables
```bash
# Database
DB_HOST=localhost           # 'database' in Docker
DB_PORT=3306
DB_NAME=clash_deck_builder
DB_USER=clash_user
DB_PASSWORD=your_password
DB_ROOT_PASSWORD=root_password

# Clash Royale API
CLASH_ROYALE_API_KEY=your_api_key

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# JWT
JWT_SECRET_KEY=your-32-char-minimum-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Application
ENVIRONMENT=development  # development, docker, production
DEBUG=true
LOG_LEVEL=debug
REACT_APP_API_BASE_URL=http://localhost:8000
```

## Important Implementation Details

### Authentication Flow
1. Google OAuth login via `@react-oauth/google`
2. Backend validates Google token and issues JWT
3. JWT stored in localStorage via `authService.ts`
4. Protected routes use `ProtectedRoute.tsx` component
5. API calls include `Authorization: Bearer {token}` header
6. Graceful fallback to anonymous mode for deck building

### Deck Management
- **Frontend format**: `{ slots: DeckSlot[] }` where `DeckSlot = { card: Card, isEvolution: boolean }`
- **Backend format**: `{ cards: Card[], evolution_slots: Card[] }`
- Transformation happens in `api.ts` `fetchDecks()` and before `createDeck()`
- Evolution cards are tracked separately in `evolution_slots`
- Anonymous users can build decks using localStorage
- Authenticated users persist decks to MySQL

### Database Schema
- **users** - User profiles with Google OAuth data
- **cards** - Clash Royale card data (name, elixir_cost, rarity, type, etc.)
- **decks** - Saved deck metadata
- **deck_cards** - Many-to-many relationship with `is_evolution` flag
- Migrations tracked in `schema_migrations` table

### Testing Strategy
- **Backend**: pytest with async support, fixtures in `tests/conftest.py`
- **Frontend**: Jest + React Testing Library
- **Contract tests**: `tests/contract/` verify API contract compliance
- **Integration tests**: Test full workflows with real database

## Common Development Patterns

### Adding a New Backend Endpoint
1. Create route handler in `src/api/[module].py`
2. Implement business logic in `src/services/[module]_service.py`
3. Add data model if needed in `src/models/`
4. Add tests in `tests/unit/` and `tests/contract/`
5. Update API documentation (FastAPI auto-generates from docstrings)

### Adding a New Frontend Component
1. Create component file in `src/components/[Component].tsx`
2. Create corresponding CSS in `src/styles/[Component].css`
3. Add service functions in `src/services/` if API calls needed
4. Add tests in same directory as `[Component].test.tsx`
5. Import and use in parent components

### Database Schema Changes
1. Create migration file in `database/migrations/` with format `YYYYMMDD_HHMMSS_description.sql`
2. Create rollback file as `YYYYMMDD_HHMMSS_description.rollback.sql`
3. Run migration: `cd database/migrations && python migrate.py`
4. Update models in `backend/src/models/`

## Running Tests

### Backend Tests
```bash
cd backend

# All tests
uv run pytest

# Specific test file
uv run pytest tests/unit/test_card_service.py

# Specific test
uv run pytest tests/unit/test_card_service.py::test_function_name

# With coverage
uv run pytest --cov=src --cov-report=html

# Integration tests (requires database)
uv run pytest tests/integration/
```

### Frontend Tests
```bash
cd frontend

# Interactive watch mode
npm test

# Run once
npm run test:run

# With coverage
npm test -- --coverage
```

## Troubleshooting

### Backend won't start
- Check database is running: `docker-compose ps`
- Verify environment variables in `backend/src/utils/config.py`
- Check database connection: `docker-compose exec database mysql -u clash_user -p`
- View logs: `docker-compose logs -f backend`

### Frontend can't connect to backend
- Verify `REACT_APP_API_BASE_URL=http://localhost:8000` in frontend environment
- Check backend health: `curl http://localhost:8000/health`
- Check CORS configuration in `backend/src/main.py`
- Verify backend is running on port 8000

### Database migration fails
- Ensure database is running and accessible
- Check migration file syntax
- Review migration logs in `database/migrations/logs/`
- Manually verify schema state: `docker-compose exec database mysql -u root -p`

### Tests failing
- Backend: Ensure test database is configured in `tests/conftest.py`
- Frontend: Clear jest cache: `npm test -- --clearCache`
- Check test fixtures and mock data are up to date

## Development Workflow

### Typical Development Session
```bash
# 1. Start database
docker-compose up -d database

# 2. Start backend (in one terminal)
cd backend
uv run uvicorn src.main:app --reload

# 3. Start frontend (in another terminal)
cd frontend
npm start

# 4. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Making Changes
1. Create feature branch from `001-i-would-like` (main development branch)
2. Make changes and test locally
3. Run linters: `uv run black . && uv run flake8 .` (backend) or verify TypeScript compiles (frontend)
4. Run tests: `uv run pytest` (backend) and `npm test` (frontend)
5. Commit and push changes
6. Create PR to `001-i-would-like` branch

**Note**: The main development branch is `001-i-would-like`, not `main`. This follows the spec-based branching strategy used by this project.

## Key Files to Know

- `backend/src/main.py` - FastAPI application factory, CORS, route registration
- `backend/src/utils/config.py` - All backend configuration via Pydantic Settings
- `backend/src/utils/database.py` - Database connection pool manager
- `frontend/src/App.tsx` - Main application component, routing setup
- `frontend/src/services/api.ts` - All backend API calls, error handling, retry logic
- `frontend/src/contexts/AuthContext.tsx` - Authentication state management
- `docker-compose.yml` - Container orchestration configuration
- `.env.docker` - Docker environment variables

## Project Management

### Kiro Integration
This project uses Kiro for project management and workflow automation:
- **Specs**: Located in `.kiro/specs/` - feature specifications and task tracking
- **Steering docs**: Located in `.kiro/steering/` - product, technical, and project guidelines
- **Hooks**: Located in `.kiro/hooks/` - automated workflows (e.g., feature branch creation)

Key steering documents:
- `.kiro/steering/product.md` - Product vision and requirements
- `.kiro/steering/tech.md` - Technology stack and standards
- `.kiro/steering/project-guide.md` - Development workflow guidelines

### Branch Strategy
- **Main development branch**: `001-i-would-like` (not `main`)
- Feature branches created from `001-i-would-like`
- PRs merge back into `001-i-would-like`
- Follows spec-based branching pattern from `.kiro/specs/`

## Notes for AI Assistants

- Always use `uv` for Python package management, never `pip` directly
- Backend uses mysql-connector-python, NOT SQLAlchemy
- Frontend uses React 19.2+ which has different patterns than older versions
- Database operations use `db_manager` from `utils/database.py`
- Configuration is centralized in `config.py` (backend) and `config.ts` (frontend)
- All API routes are prefixed with `/api/`
- Evolution slots are a critical feature - always maintain the distinction between regular cards and evolution cards
- Anonymous users can build decks without authentication using localStorage
- Database migrations are standalone scripts (use `python migrate.py`), not part of the backend package

## External Integrations

### Clash Royale API
- Card data ingestion via `backend/src/scripts/ingest_cards.py`
- API client in `backend/src/services/clash_api_service.py`
- Requires `CLASH_ROYALE_API_KEY` environment variable
- Card data stored in MySQL `cards` table

### Google OAuth
- Frontend: `@react-oauth/google` package
- Backend: Google Auth library for token validation
- JWT tokens for session management
- User data stored in MySQL `users` table
