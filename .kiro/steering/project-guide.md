---
inclusion: always
---

# Clash Royale Deck Builder - Development Guide

## Product Context
A web application for building and managing Clash Royale decks with card filtering, deck persistence, and Google OAuth authentication.

**Core Business Rules:**
- Maximum 20 saved decks per user
- Decks support up to 2 evolution card slots
- Real-time average elixir calculation
- All deck data persists in MySQL database

## Technology Stack

### Backend (Python FastAPI)
- **Python 3.11+** with **UV package manager**
- **FastAPI** with Uvicorn ASGI server
- **MySQL** with mysql-connector-python
- **httpx** for external API calls
- **pytest** with pytest-asyncio for testing

### Frontend (React TypeScript)
- **React 19.2+** with Create React App
- **TypeScript** in strict mode
- **React Router DOM** for routing
- **Jest + React Testing Library** for testing

## Architecture Patterns

### Backend Structure
```
backend/src/
├── api/          # FastAPI route handlers
├── models/       # Database models and schema
├── services/     # Business logic and external integrations
├── utils/        # Configuration and utilities
└── middleware/   # Authentication and request processing
```

**Key Principles:**
- Layered architecture: API → Services → Models
- Use FastAPI dependency injection for database connections
- Separate business logic from HTTP handling

### Frontend Structure
```
frontend/src/
├── components/   # React components
├── contexts/     # React contexts (Auth, Onboarding)
├── services/     # API clients and external integrations
├── styles/       # Component-specific CSS files
└── tests/        # Test files
```

**Key Principles:**
- Component-based architecture with TypeScript-first approach
- Service layer for API calls and business logic
- Context providers for global state management

## Development Standards

### Code Style
- **Backend**: Snake case for Python files (`auth_service.py`)
- **Frontend**: PascalCase for components (`DeckBuilder.tsx`), camelCase for utilities
- **Tests**: Mirror source structure with `.test.` or `.integration.test.` suffix

### Testing Requirements
- Backend: Use pytest with async support
- Frontend: Jest + React Testing Library for unit and integration tests
- Always test authentication flows and deck management features

### Environment Configuration
- Backend API: Port 8000 (configurable via `backend/src/utils/config.py`)
- Frontend dev server: Port 3000
- Set `REACT_APP_API_BASE_URL=http://localhost:8000` in frontend environment
- Google OAuth credentials configured via environment variables

## Common Development Commands

### Backend
```bash
cd backend
uv install                           # Install dependencies
uv run uvicorn main:app --reload     # Start dev server
uv run pytest                       # Run tests
uv run black . && uv run flake8 .   # Format and lint
```

### Frontend
```bash
cd frontend
npm install     # Install dependencies
npm start       # Start dev server
npm test        # Run tests
npm run build   # Production build
```

## Key Integration Points
- **Clash Royale API**: External card data integration
- **Google OAuth**: User authentication and profile management
- **MySQL Database**: Persistent deck storage with migration support
- **Local Storage**: Anonymous deck storage fallback

## Authentication Flow
- Google OAuth for user authentication
- JWT tokens for API authorization
- Protected routes with authentication middleware
- Graceful fallback to anonymous mode for deck building