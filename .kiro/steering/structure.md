# Project Structure

## Root Directory Layout
```
clash_deck_builder/
├── backend/           # Python FastAPI backend
├── frontend/          # React TypeScript frontend
├── docs/             # API documentation
├── specs/            # Feature specifications
├── .kiro/            # Kiro AI assistant configuration
├── .specify/         # Specify tool configuration
└── README.md         # Main project documentation
```

## Backend Structure (`backend/`)
```
backend/
├── src/
│   ├── api/          # FastAPI route handlers and endpoints
│   ├── models/       # Database models and schema definitions
│   ├── services/     # Business logic and external API integrations
│   └── utils/        # Utility functions and configuration
├── tests/            # Backend test suite
├── pyproject.toml    # Python dependencies and project config
├── uv.lock          # Locked dependency versions
└── .python-version   # Python version specification
```

## Frontend Structure (`frontend/`)
```
frontend/
├── src/
│   ├── components/   # React components
│   ├── services/     # API client and external service integrations
│   ├── App.tsx       # Main application component
│   └── index.tsx     # Application entry point
├── public/           # Static assets
├── tests/            # Frontend test suite
├── package.json      # Node.js dependencies and scripts
└── tsconfig.json     # TypeScript configuration
```

## Architecture Patterns

### Backend (FastAPI)
- **Layered Architecture**: API → Services → Models
- **Separation of Concerns**: Routes handle HTTP, services contain business logic, models define data structure
- **Dependency Injection**: Use FastAPI's built-in DI for database connections and external services

### Frontend (React)
- **Component-Based Architecture**: Reusable UI components in `components/`
- **Service Layer**: API calls and external integrations in `services/`
- **TypeScript First**: Strict typing for all components and data structures

## File Naming Conventions
- **Backend**: Snake case for Python files (`clash_api_service.py`)
- **Frontend**: PascalCase for components (`DeckBuilder.tsx`), camelCase for utilities
- **Tests**: Mirror source structure with `.test.` suffix

## Key Configuration Files
- `backend/src/utils/config.py` - Database and API configuration
- `frontend/.env` - Environment variables for API endpoints
- `backend/src/models/schema.sql` - Database schema definitions