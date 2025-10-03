# Development Guide

This guide covers different development workflows for the Clash Royale Deck Builder application.

## Prerequisites

- **Docker & Docker Compose**: For containerized development
- **Node.js 16+**: For frontend development
- **Python 3.11+**: For local backend development (optional)
- **UV**: Python package manager for backend dependencies

## Development Workflows

### 1. Full Containerized Development (Recommended)

Run both backend and database in containers while developing the frontend locally.

#### Setup
```bash
# 1. Clone the repository
git clone <repository-url>
cd clash_deck_builder

# 2. Set up environment files
./scripts/setup-env.sh

# 3. Update .env.docker with your Clash Royale API key
# Edit .env.docker and replace CLASH_ROYALE_API_KEY with your actual key

# 4. Start the containerized backend and database
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 5. Install frontend dependencies
cd frontend
npm install

# 6. Start the frontend development server
npm start
```

#### Workflow
- **Backend**: Runs in container with hot reload enabled
- **Database**: Runs in container with persistent data
- **Frontend**: Runs locally with hot reload
- **API Calls**: Frontend connects to `http://localhost:8000`

#### Useful Commands
```bash
# View container logs
docker-compose logs -f backend
docker-compose logs -f database

# Restart backend container
docker-compose restart backend

# Stop all containers
docker-compose down

# Stop containers and remove volumes (fresh start)
docker-compose down -v
```

### 2. Frontend-Only Development

Develop frontend against a running containerized backend.

#### Setup
```bash
# 1. Start backend and database containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend database

# 2. Install and start frontend
cd frontend
npm install
npm start
```

#### Use Case
- Frontend feature development
- UI/UX improvements
- Component testing

### 3. Backend-Only Development

Develop backend with containerized database.

#### Setup
```bash
# 1. Start only the database container
docker-compose up -d database

# 2. Set up local backend environment
cd backend
uv install

# 3. Use .env.local for local backend configuration
cp ../.env.local .env

# 4. Update database host in .env to localhost
# Edit .env and set DB_HOST=localhost

# 5. Start backend locally
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Use Case
- Backend API development
- Database integration testing
- Performance optimization

### 4. Fully Local Development

Run everything locally without containers.

#### Prerequisites
- MySQL 8.0+ installed locally
- Database created and configured

#### Setup
```bash
# 1. Set up local database
mysql -u root -p
CREATE DATABASE clash_deck_builder_dev;
CREATE USER 'clash_user'@'localhost' IDENTIFIED BY 'local_password';
GRANT ALL PRIVILEGES ON clash_deck_builder_dev.* TO 'clash_user'@'localhost';

# 2. Run database initialization scripts
mysql -u clash_user -p clash_deck_builder_dev < database/init/01-schema.sql
mysql -u clash_user -p clash_deck_builder_dev < database/init/02-indexes.sql
mysql -u clash_user -p clash_deck_builder_dev < database/init/03-seed-data.sql

# 3. Start backend
cd backend
cp ../.env.local .env
uv install
uv run uvicorn main:app --reload

# 4. Start frontend
cd frontend
npm install
npm start
```

## Environment Configuration

### Frontend Environment Files

- **`.env`**: Default configuration for containerized backend
- **`.env.local`**: Local development configuration
- **`.env.docker`**: Docker-specific configuration with polling enabled

### Backend Environment Files

- **`.env.local`**: Local development with safe defaults
- **`.env.docker`**: Docker container configuration
- **`.env`**: Production configuration (create from .env.example)

### Environment Variables

#### Frontend
- `REACT_APP_API_BASE_URL`: Backend API URL (default: http://localhost:8000)
- `PORT`: Frontend development server port (default: 3000)
- `GENERATE_SOURCEMAP`: Enable source maps for debugging
- `WATCHPACK_POLLING`: Enable file watching in Docker (Docker only)

#### Backend
- `DB_HOST`: Database host (localhost for local, database for Docker)
- `DB_PORT`: Database port (default: 3306)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `CLASH_ROYALE_API_KEY`: Your Clash Royale API key
- `CORS_ORIGINS`: Allowed frontend origins
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level

## Development Commands

### Docker Commands
```bash
# Start full stack
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start specific services
docker-compose up -d database
docker-compose up -d backend

# View logs
docker-compose logs -f [service-name]

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec database mysql -u root -p

# Clean up
docker-compose down
docker-compose down -v  # Remove volumes too
```

### Backend Commands
```bash
cd backend

# Install dependencies
uv install

# Start development server
uv run uvicorn main:app --reload

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run flake8 .

# Database migrations (if implemented)
uv run python -m database.migrations.migrate
```

### Frontend Commands
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

# Run tests with coverage
npm test -- --coverage --watchAll=false
```

## Troubleshooting

### Docker Environment Issues

#### Container Startup Problems

**Backend container won't start:**
```bash
# 1. Check container logs for errors
docker-compose logs backend

# 2. Check if database is ready
docker-compose ps
# Look for "healthy" status on database service

# 3. Verify environment variables
docker-compose config
# Check if all required variables are set

# 4. Rebuild container if code changes aren't reflected
docker-compose build backend --no-cache

# 5. Check for port conflicts
docker ps -a
# Ensure no other containers are using port 8000
```

**Database container won't start:**
```bash
# 1. Check database logs
docker-compose logs database

# 2. Common issues and solutions:
# - Port 3306 already in use (local MySQL running)
sudo systemctl stop mysql  # Linux
brew services stop mysql   # macOS

# - Insufficient disk space
docker system df
docker system prune  # Clean up unused containers/images

# 3. Reset database completely
docker-compose down -v
docker volume rm clash_deck_builder_mysql_data
docker-compose up -d database
```

**Services fail to communicate:**
```bash
# 1. Check Docker network
docker network ls
docker network inspect clash_deck_builder_clash-network

# 2. Test connectivity between containers
docker-compose exec backend ping database
docker-compose exec backend curl http://database:3306

# 3. Verify service names in docker-compose.yml match connection strings
```

#### Environment Configuration Issues

**Environment variables not loading:**
```bash
# 1. Check if .env files exist
ls -la .env*

# 2. Verify file format (no spaces around =)
cat .env.docker | grep -v "^#" | grep "="

# 3. Check docker-compose env_file configuration
docker-compose config | grep -A 5 env_file

# 4. Test environment variable injection
docker-compose exec backend env | grep DB_
```

**API key or database credentials issues:**
```bash
# 1. Verify API key format
echo $CLASH_ROYALE_API_KEY | wc -c
# Should be around 100+ characters

# 2. Test database credentials
docker-compose exec database mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME

# 3. Check for special characters in passwords
# Escape special characters in .env files: password\!123
```

#### Network and Connectivity Issues

**Frontend can't reach backend:**
```bash
# 1. Check backend health endpoint
curl http://localhost:8000/health

# 2. Verify backend is listening on correct port
docker-compose exec backend netstat -tlnp | grep 8000

# 3. Check CORS configuration
docker-compose logs backend | grep -i cors

# 4. Test from within Docker network
docker-compose exec backend curl http://localhost:8000/health
```

**Database connection timeouts:**
```bash
# 1. Check database health
docker-compose exec database mysqladmin ping -h localhost

# 2. Verify connection parameters
docker-compose exec backend env | grep DB_

# 3. Test connection from backend container
docker-compose exec backend python -c "
import mysql.connector
conn = mysql.connector.connect(
    host='database', user='$DB_USER', 
    password='$DB_PASSWORD', database='$DB_NAME'
)
print('Connection successful')
"

# 4. Check for connection pool exhaustion
docker-compose logs backend | grep -i "connection"
```

#### Performance and Resource Issues

**Slow container startup:**
```bash
# 1. Check Docker resource allocation
docker stats

# 2. Increase Docker memory/CPU limits
# Docker Desktop: Settings > Resources

# 3. Check for resource-intensive processes
docker-compose exec backend top
docker-compose exec database top

# 4. Optimize Docker build cache
docker-compose build --no-cache
docker system prune -a
```

**High memory usage:**
```bash
# 1. Monitor container resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 2. Check for memory leaks in application
docker-compose logs backend | grep -i "memory\|oom"

# 3. Adjust container memory limits
# Add to docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

**File watching issues (Windows/macOS):**
```bash
# 1. Enable polling for file changes
# Add to frontend/.env.docker:
echo "WATCHPACK_POLLING=true" >> frontend/.env.docker
echo "CHOKIDAR_USEPOLLING=true" >> frontend/.env.docker

# 2. Increase polling interval if CPU usage is high
echo "CHOKIDAR_INTERVAL=1000" >> frontend/.env.docker

# 3. Use bind mounts instead of volumes for development
# In docker-compose.dev.yml, ensure:
# volumes:
#   - ./backend/src:/app/src
```

#### Data and Volume Issues

**Database data not persisting:**
```bash
# 1. Check if volume is properly mounted
docker volume ls | grep mysql
docker volume inspect clash_deck_builder_mysql_data

# 2. Verify volume mount in container
docker-compose exec database df -h | grep mysql

# 3. Check file permissions
docker-compose exec database ls -la /var/lib/mysql
```

**Migration or initialization issues:**
```bash
# 1. Check if init scripts ran
docker-compose logs database | grep -i "init\|schema"

# 2. Manually run initialization scripts
docker-compose exec database mysql -u root -p$DB_ROOT_PASSWORD $DB_NAME < /docker-entrypoint-initdb.d/01-schema.sql

# 3. Reset database and re-initialize
docker-compose down -v
docker-compose up -d database
# Wait for initialization to complete
docker-compose logs -f database
```

#### Security and Permission Issues

**Permission denied errors:**
```bash
# 1. Check file ownership
ls -la backend/
ls -la database/

# 2. Fix ownership if needed (Linux/macOS)
sudo chown -R $USER:$USER backend/
sudo chown -R $USER:$USER database/

# 3. Check Docker daemon permissions
groups $USER | grep docker
# If not in docker group: sudo usermod -aG docker $USER
```

**SSL/TLS certificate issues:**
```bash
# 1. For development, disable SSL verification
# Add to backend environment:
PYTHONHTTPSVERIFY=0

# 2. Check certificate validity
openssl s_client -connect api.clashroyale.com:443

# 3. Update CA certificates in container
docker-compose exec backend apt-get update && apt-get install -y ca-certificates
```

### Common Error Messages and Solutions

#### "Connection refused" errors
```bash
# Cause: Service not ready or wrong host/port
# Solution: Wait for service health check, verify connection parameters
docker-compose ps  # Check service status
docker-compose logs [service-name]  # Check for startup errors
```

#### "No such file or directory" errors
```bash
# Cause: Missing files or incorrect volume mounts
# Solution: Check file paths and volume configuration
docker-compose exec [service] ls -la /path/to/file
```

#### "Port already in use" errors
```bash
# Cause: Another service using the same port
# Solution: Stop conflicting service or change port
sudo lsof -i :8000  # Find process using port
sudo kill -9 [PID]  # Kill process
# Or change port in docker-compose.yml
```

#### "Authentication failed" errors
```bash
# Cause: Wrong database credentials or API keys
# Solution: Verify credentials in environment files
docker-compose exec backend env | grep -E "(DB_|API_KEY)"
```

### Diagnostic Commands

**Complete system check:**
```bash
#!/bin/bash
echo "=== Docker System Info ==="
docker --version
docker-compose --version
docker system df

echo "=== Container Status ==="
docker-compose ps

echo "=== Network Info ==="
docker network ls | grep clash

echo "=== Volume Info ==="
docker volume ls | grep clash

echo "=== Service Health ==="
curl -s http://localhost:8000/health || echo "Backend not responding"
docker-compose exec database mysqladmin ping -h localhost || echo "Database not responding"

echo "=== Recent Logs ==="
docker-compose logs --tail=10 backend
docker-compose logs --tail=10 database
```

**Performance monitoring:**
```bash
# Monitor resource usage
watch -n 1 'docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"'

# Monitor logs in real-time
docker-compose logs -f --tail=50
```

### Recovery Procedures

**Complete environment reset:**
```bash
# 1. Stop all services
docker-compose down

# 2. Remove all containers and volumes
docker-compose down -v
docker system prune -a

# 3. Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# 4. Verify services are healthy
docker-compose ps
curl http://localhost:8000/health
```

**Database recovery:**
```bash
# 1. Backup current data (if possible)
./scripts/backup-database.sh

# 2. Reset database
docker-compose down database
docker volume rm clash_deck_builder_mysql_data

# 3. Restore from backup
docker-compose up -d database
./scripts/restore-database.sh [backup-file]
```

## Testing

### Backend Testing
```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_api.py

# Run tests with database
docker-compose up -d database
uv run pytest tests/test_database.py
```

### Frontend Testing
```bash
cd frontend

# Run tests
npm test

# Run tests once (CI mode)
npm test -- --run

# Run with coverage
npm test -- --coverage --watchAll=false
```

### Integration Testing
```bash
# Start full stack
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for services to be ready
sleep 10

# Run integration tests
cd backend
uv run pytest tests/integration/

# Or test API endpoints manually
curl http://localhost:8000/health
curl http://localhost:8000/cards
```

## Production Deployment

### Environment Setup
```bash
# 1. Create production environment file
cp .env.example .env

# 2. Update with production values
# - Secure database passwords
# - Real Clash Royale API key
# - Production CORS origins
# - Disable debug mode

# 3. Deploy with production compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Security Considerations
- Use strong, unique passwords
- Enable SSL/TLS in production
- Restrict CORS origins to your domain
- Use secrets management for sensitive data
- Regular security updates for base images

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [Clash Royale API Documentation](https://developer.clashroyale.com/)