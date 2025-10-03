# Clash Royale Deck Builder

This project implements a Clash Royale deck builder with a simple UI, allowing users to build, save, and manage their decks.

## Features
- Display all Clash Royale cards with correct rarity and formatting.
- Filter cards by elixir, name, rarity, arena, and type.
- Build decks with up to 2 evolution card slots and average elixir calculation.
- Save, rename, and delete up to 20 decks.
- Persistence of decks in a MySQL database.

## Quick Start (Recommended)

The easiest way to get started is using Docker for the backend and database:

```bash
# 1. Set up the development environment
./scripts/dev-setup.sh setup          # Linux/macOS
# OR
.\scripts\dev-setup.ps1 setup         # Windows

# 2. Start the containerized backend and database
./scripts/dev-setup.sh containerized  # Linux/macOS
# OR
.\scripts\dev-setup.ps1 containerized # Windows

# 3. In a new terminal, start the frontend
cd frontend
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Database**: localhost:3306

## Development Workflows

This project supports multiple development workflows. See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed instructions.

### 1. Full Containerized Development (Recommended)
- Backend and database run in Docker containers
- Frontend runs locally with hot reload
- Best for most development scenarios

### 2. Frontend-Only Development
- Use when working on UI/UX improvements
- Requires containerized backend to be running

### 3. Backend-Only Development
- Use when working on API features
- Database runs in container, backend runs locally

### 4. Fully Local Development
- Everything runs locally without Docker
- Requires local MySQL installation

## Prerequisites

### For Containerized Development (Recommended)
- **Docker & Docker Compose**: For running backend and database
- **Node.js 16+**: For frontend development
- **Clash Royale API Key**: Get from [developer.clashroyale.com](https://developer.clashroyale.com/)

### For Local Development
- **Python 3.11+**: For backend development
- **UV**: Python package manager
- **Node.js 16+**: For frontend development
- **MySQL 8.0+**: Database server
- **Clash Royale API Key**: Get from [developer.clashroyale.com](https://developer.clashroyale.com/)

## Manual Setup (Alternative)

If you prefer to set up the environment manually or the scripts don't work for your system:

### Environment Configuration
1. Copy environment template:
   ```bash
   cp .env.example .env.docker
   ```
2. Update `.env.docker` with your Clash Royale API key
3. Create frontend environment:
   ```bash
   echo "REACT_APP_API_BASE_URL=http://localhost:8000" > frontend/.env
   ```

### Backend Setup (Containerized)
```bash
# Start backend and database containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Local Backend Setup (Alternative)
If you prefer to run the backend locally:

```bash
# Start only the database container
docker-compose up -d database

# Set up backend
cd backend
uv install
cp ../.env.local .env
# Edit .env and set DB_HOST=localhost
uv run uvicorn main:app --reload
```

## Development Commands

### Quick Commands
```bash
# Check development environment status
./scripts/dev-setup.sh status          # Linux/macOS
.\scripts\dev-setup.ps1 status         # Windows

# Stop all services
./scripts/dev-setup.sh stop            # Linux/macOS
.\scripts\dev-setup.ps1 stop           # Windows

# Clean up (remove containers and volumes)
./scripts/dev-setup.sh cleanup         # Linux/macOS
.\scripts\dev-setup.ps1 cleanup        # Windows
```

### Docker Commands
```bash
# View container logs
docker-compose logs -f backend
docker-compose logs -f database

# Restart a service
docker-compose restart backend

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec database mysql -u root -p
```

### Backend Development
```bash
cd backend

# Install dependencies
uv install

# Start development server (local)
uv run uvicorn main:app --reload

# Run tests
uv run pytest

# Format and lint code
uv run black .
uv run flake8 .
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Troubleshooting

### Quick Fixes

**Backend container won't start:**
```bash
# Check logs for errors
docker-compose logs backend

# Rebuild container if needed
docker-compose build backend --no-cache

# Verify database is healthy first
docker-compose ps
```

**Database connection issues:**
```bash
# Check database health
docker-compose exec database mysqladmin ping -h localhost

# Reset database if corrupted
docker-compose down -v
docker-compose up -d database
```

**Frontend can't connect to backend:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check frontend environment
cat frontend/.env
# Should contain: REACT_APP_API_BASE_URL=http://localhost:8000

# Check CORS configuration
docker-compose logs backend | grep -i cors
```

**Port conflicts:**
```bash
# Check what's using the ports
netstat -tulpn | grep -E "(3000|8000|3306)"  # Linux/macOS
netstat -an | findstr ":3000 :8000 :3306"   # Windows

# Stop conflicting services
sudo systemctl stop mysql  # Linux
brew services stop mysql   # macOS
```

**Environment variable issues:**
```bash
# Verify all required variables are set
docker-compose config

# Check variables in running container
docker-compose exec backend env | grep -E "(DB_|CLASH_|CORS_)"
```

### Complete System Reset
If you're experiencing persistent issues:
```bash
# Stop everything and clean up
docker-compose down -v
docker system prune -f

# Rebuild from scratch
docker-compose build --no-cache
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Verify services are healthy
./scripts/dev-setup.sh status  # Linux/macOS
.\scripts\dev-setup.ps1 status # Windows
```

### Comprehensive Troubleshooting
For detailed troubleshooting guides covering Docker-specific issues, performance problems, and recovery procedures, see:
- [DOCKER.md](DOCKER.md) - Complete Docker troubleshooting guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development workflows and common issues

## Project Structure

```
clash_deck_builder/
├── backend/              # Python FastAPI backend
│   ├── src/             # Application source code
│   ├── tests/           # Backend tests
│   └── Dockerfile       # Backend container configuration
├── frontend/            # React TypeScript frontend
│   ├── src/             # Frontend source code
│   └── tests/           # Frontend tests
├── database/            # Database configuration
│   ├── init/            # Database initialization scripts
│   ├── migrations/      # Schema migration scripts
│   └── backups/         # Database backup storage
├── scripts/             # Development and deployment scripts
├── docker-compose.yml   # Main Docker configuration
├── docker-compose.dev.yml   # Development overrides
├── docker-compose.prod.yml  # Production overrides
└── DEVELOPMENT.md       # Detailed development guide
```

## API Documentation

When the backend is running, you can access:
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test them
4. Run linting and tests: `./scripts/dev-setup.sh status`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
