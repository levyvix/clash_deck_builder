# Technology Stack

## Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Package Manager**: UV (modern Python package manager)
- **Database**: MySQL with mysql-connector-python
- **HTTP Client**: httpx for external API calls
- **ASGI Server**: Uvicorn

## Frontend
- **Language**: TypeScript
- **Framework**: React 19.2+ with Create React App
- **Routing**: React Router DOM
- **Testing**: Jest + React Testing Library
- **Build Tool**: React Scripts (Webpack under the hood)

## External APIs
- **Clash Royale API**: For card data and game information

## Development Tools
- **Python Linting**: Black (formatting) + Flake8 (linting)
- **Testing**: pytest with pytest-asyncio for backend
- **TypeScript**: Strict mode enabled with comprehensive type checking

## Common Commands

### Backend Development
```bash
cd backend
uv install                    # Install dependencies
uv run uvicorn main:app --reload  # Start development server
uv run black .               # Format code
uv run flake8 .              # Lint code
uv run pytest               # Run tests
```

### Frontend Development
```bash
cd frontend
npm install                  # Install dependencies
npm start                   # Start development server (port 3000)
npm test                    # Run tests
npm run build               # Build for production
```

## Environment Configuration
- Backend API runs on port 8000 by default
- Frontend development server runs on port 3000
- Set `REACT_APP_API_BASE_URL=http://localhost:8000` in frontend/.env
- Configure MySQL connection in `backend/src/utils/config.py`
- Set Clash Royale API key in environment or `backend/src/services/clash_api_service.py`