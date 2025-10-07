# Development Environment Setup

This guide will help you set up your development environment for the Clash Royale Deck Builder project.

## Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 2GB free space
- **Docker**: Required for containerized development

### Required Software
1. [Git](https://git-scm.com/downloads) (v2.30+)
2. [Node.js](https://nodejs.org/) (v18+ LTS)
3. [Python](https://www.python.org/downloads/) (v3.11+)
4. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v20.10+)
5. [VS Code](https://code.visualstudio.com/) (recommended) or your preferred IDE

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/clash-royale-deck-builder.git
cd clash-royale-deck-builder
```

### 2. Backend Setup

#### Option A: Using Docker (Recommended)
```bash
# Start backend and database containers
docker-compose up -d backend database

# Install Python dependencies
docker-compose exec backend pip install -e .[dev]

# Run database migrations
docker-compose exec backend alembic upgrade head
```

#### Option B: Local Python Environment
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the database
docker-compose up -d database

# Run migrations
alembic upgrade head

# Start the development server
uvicorn src.main:app --reload
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Configure Environment
```bash
cp .env.example .env.local
# Edit .env.local with your backend URL
```

#### Start Development Server
```bash
npm start
```

## Development Workflows

### Running the Full Stack
```bash
# In project root
docker-compose up -d  # Start all services
cd frontend && npm start  # Start frontend dev server
```

### Running Tests

#### Backend Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_deck_service.py

# Run with coverage
pytest --cov=src tests/
```

#### Frontend Tests
```bash
# Unit tests
npm test

# E2E tests
npm run test:e2e
```

### Database Management

#### Run Migrations
```bash
alembic revision --autogenerate -m "Your migration message"
alembic upgrade head
```

#### Database Reset
```bash
# WARNING: This will delete all data!
docker-compose down -v
docker-compose up -d database
```

## Development Tools

### VS Code Extensions (Recommended)
- Python
- ESLint
- Prettier
- Docker
- GitLens
- REST Client

### API Testing
Use the `requests.http` file in the root directory with the REST Client extension:
```http
# @name login
POST http://localhost:8000/api/auth/google
Content-Type: application/json

{
  "credential": "your_google_token"
}

###
@authToken = {{login.response.body.access_token}}

GET http://localhost:8000/api/decks
Authorization: Bearer {{authToken}}
```

## Common Issues

### Port Conflicts
If you encounter port conflicts, check which process is using the port:
```bash
# On Linux/macOS
lsof -i :8000

# On Windows
netstat -ano | findstr :8000
```

### Database Connection Issues
1. Ensure Docker is running
2. Check if the database container is up: `docker ps`
3. Verify credentials in `.env` match those in `docker-compose.yml`

### Frontend Not Connecting to Backend
1. Check that the backend is running
2. Verify `REACT_APP_API_URL` in `.env.local` points to the correct backend URL
3. Check for CORS errors in the browser console

## Environment Variables

### Backend (`.env`)
```ini
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/clash_royale
TEST_DATABASE_URL=mysql+pymysql://user:password@localhost:3306/test_clash_royale

# Authentication
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
FRONTEND_URL=http://localhost:3000

# Logging
LOG_LEVEL=INFO

# Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=86400  # 24 hours
```

### Frontend (`.env.local`)
```ini
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
```

## Next Steps

1. Run the test suite to verify your setup
2. Check out the [Development Workflow](development-workflow.md) guide
3. Take a look at the [Code Style Guide](code-style.md)
4. Pick an issue from the [Issue Tracker](https://github.com/yourusername/clash-royale-deck-builder/issues)

## Getting Help

If you encounter any issues during setup:
1. Check the [Troubleshooting](#troubleshooting) section
2. Search the [GitHub Issues](https://github.com/yourusername/clash-royale-deck-builder/issues)
3. Open a new issue if your problem isn't documented
