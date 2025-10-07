# Quick Start Guide

Get the Clash Royale Deck Builder running locally in minutes.

## Prerequisites

- **Python 3.11+** installed
- **Node.js 16+** and npm installed
- **Docker** and Docker Compose (recommended)
- **Git** for version control

## Option 1: Docker (Recommended)

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd clash_deck_builder

# Copy environment template
cp .env.template .env

# Edit .env with your API keys (see Environment Setup)
nano .env

# Start all services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for services to be ready (about 30 seconds)
# Check status
docker-compose ps

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Option 2: Local Development

For local development without Docker:

### 1. Setup Database

```bash
# Start only the database container
docker-compose up -d database

# Or install MySQL locally
# Ubuntu/Debian
sudo apt install mysql-server

# macOS
brew install mysql
brew services start mysql
```

### 2. Setup Backend

```bash
cd backend

# Install UV package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
cd ../database/migrations
python migrate.py

# Ingest card data from Clash Royale API
cd ../../backend
uv run src/scripts/ingest_cards.py

# Start backend server
uv run uvicorn src.main:app --reload
```

Backend will be available at `http://localhost:8000`

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at `http://localhost:3000`

## Initial Configuration

### Required API Keys

You'll need to obtain these API keys:

1. **Google OAuth Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable Google Identity Services
   - Create OAuth 2.0 credentials
   - See [Environment Setup](environment-setup.md#google-oauth-setup) for details

2. **Clash Royale API Key**
   - Visit [Clash Royale Developer Portal](https://developer.clashroyale.com/)
   - Create an account and generate an API key
   - See [Environment Setup](environment-setup.md#clash-royale-api-setup) for details

### Environment Variables

Edit your `.env` file with these minimum required variables:

```bash
# Database
DB_HOST=localhost  # or 'database' if using Docker
DB_PASSWORD=your_secure_password

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# Clash Royale API
CLASH_ROYALE_API_KEY=your_api_key

# JWT
JWT_SECRET_KEY=your_32_character_minimum_secret_key
```

Generate a secure JWT secret:
```bash
openssl rand -base64 32
```

## Verify Installation

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Check Database Connection

```bash
# Using Docker
docker-compose exec database mysql -u clash_user -p clash_deck_builder

# Or locally
mysql -h localhost -u clash_user -p clash_deck_builder
```

### 3. Test Frontend

Open `http://localhost:3000` in your browser. You should see:
- Card gallery with Clash Royale cards
- Deck builder interface
- Google Sign In button

### 4. View API Documentation

Open `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## Next Steps

- Read the [Development Workflow](workflow.md) guide
- Explore the [Architecture Overview](../architecture/overview.md)
- Check out [Backend Development](../development/backend.md) practices
- Learn about [Testing](../development/testing.md) strategies

## Troubleshooting

### Backend won't start
```bash
# Check database is running
docker-compose ps

# View backend logs
docker-compose logs -f backend

# Verify environment variables
cd backend
uv run python -c "from src.utils.config import settings; print(settings.dict())"
```

### Frontend can't connect to backend
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration
# CORS_ORIGINS should include http://localhost:3000
```

### Database migration fails
```bash
# Check database is accessible
docker-compose exec database mysql -u root -p

# View migration logs
cat database/migrations/logs/*.log
```

For more troubleshooting help, see [Troubleshooting Guide](../operations/troubleshooting.md).
