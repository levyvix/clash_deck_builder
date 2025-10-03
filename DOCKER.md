# Docker Setup and Troubleshooting Guide

This guide provides comprehensive information for setting up and troubleshooting the Docker-based development environment for the Clash Royale Deck Builder.

## Quick Setup

### Prerequisites
- Docker Desktop (Windows/macOS) or Docker Engine + Docker Compose (Linux)
- Git
- Node.js 16+ (for frontend development)

### Automated Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd clash_deck_builder

# Run setup script
./scripts/dev-setup.sh setup          # Linux/macOS
# OR
.\scripts\dev-setup.ps1 setup         # Windows

# Start containerized development
./scripts/dev-setup.sh containerized  # Linux/macOS
# OR
.\scripts\dev-setup.ps1 containerized # Windows
```

### Manual Setup
```bash
# 1. Set up environment files
cp .env.example .env.docker
# Edit .env.docker with your Clash Royale API key

# 2. Create frontend environment
echo "REACT_APP_API_BASE_URL=http://localhost:8000" > frontend/.env

# 3. Start services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 4. Install and start frontend
cd frontend
npm install
npm start
```

## Docker Architecture

### Services Overview
- **database**: MySQL 8.0 container with persistent storage
- **backend**: FastAPI application container with hot reload
- **frontend**: Runs locally, connects to containerized backend

### Network Configuration
```
Host Machine (localhost)
├── Frontend :3000 → Backend :8000
└── Docker Network (clash-network)
    ├── backend:8000 → database:3306
    └── database:3306 (MySQL)
```

### Volume Mounts
- `mysql_data`: Persistent database storage
- `./backend:/app`: Backend code for hot reload
- `./database/init:/docker-entrypoint-initdb.d`: Database initialization
- `./database/backups:/backups`: Backup storage

## Environment Configuration

### Environment Files Structure
```
.env.example      # Template with all variables
.env.local        # Local development (safe defaults)
.env.docker       # Docker development
.env              # Production (create from template)
```

### Required Environment Variables

#### Database Configuration
```bash
DB_ROOT_PASSWORD=secure_root_password
DB_NAME=clash_deck_builder
DB_USER=clash_user
DB_PASSWORD=secure_user_password
DB_PORT=3306
```

#### Application Configuration
```bash
CLASH_ROYALE_API_KEY=your_api_key_here
DEBUG=true                    # Development only
LOG_LEVEL=debug              # Development only
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Environment Variable Validation
```bash
# Check if all required variables are set
docker-compose config

# Verify variables in running container
docker-compose exec backend env | grep -E "(DB_|CLASH_|CORS_)"
```

## Docker Compose Configurations

### Development Configuration
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Features:
# - Hot reload enabled
# - Debug logging
# - Development seed data
# - Volume mounts for code changes
```

### Production Configuration
```bash
# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Features:
# - Optimized for performance
# - Security hardening
# - No development tools
# - Restart policies
```

### Testing Configuration
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Features:
# - Isolated test database
# - Test-specific configuration
# - Automated cleanup
```

## Common Docker Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d database

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Restart a service
docker-compose restart backend

# View service status
docker-compose ps
```

### Logs and Debugging
```bash
# View logs for all services
docker-compose logs

# Follow logs for specific service
docker-compose logs -f backend

# View last 50 lines
docker-compose logs --tail=50 database

# Search logs for errors
docker-compose logs backend | grep -i error
```

### Container Interaction
```bash
# Execute command in running container
docker-compose exec backend bash
docker-compose exec database mysql -u root -p

# Run one-time command
docker-compose run --rm backend python -c "print('Hello')"

# Copy files to/from container
docker cp file.txt clash-backend:/app/
docker cp clash-backend:/app/logs/ ./local-logs/
```

### Image and Volume Management
```bash
# Rebuild containers
docker-compose build
docker-compose build --no-cache backend

# Remove unused images and containers
docker system prune

# Remove all unused data (careful!)
docker system prune -a

# List and remove volumes
docker volume ls
docker volume rm clash_deck_builder_mysql_data
```

## Troubleshooting Guide

### Startup Issues

#### Services Won't Start
```bash
# 1. Check Docker daemon is running
docker --version
docker ps

# 2. Check for port conflicts
netstat -tulpn | grep -E "(3000|8000|3306)"
# Windows: netstat -an | findstr ":3000 :8000 :3306"

# 3. Check available disk space
docker system df
df -h  # Linux/macOS
# Windows: Check available disk space in Docker Desktop settings

# 4. Verify Docker Compose file syntax
docker-compose config
```

#### Database Container Issues
```bash
# Check database initialization
docker-compose logs database | grep -i "ready for connections"

# Common issues:
# - Port 3306 in use by local MySQL
sudo systemctl stop mysql  # Linux
brew services stop mysql   # macOS
# Windows: Stop MySQL service in Services panel

# - Insufficient permissions
ls -la database/init/
# Ensure init scripts are readable

# - Corrupted volume
docker-compose down -v
docker volume rm clash_deck_builder_mysql_data
```

#### Backend Container Issues
```bash
# Check backend startup
docker-compose logs backend | grep -i "uvicorn"

# Common issues:
# - Missing environment variables
docker-compose exec backend env | grep DB_

# - Database not ready
docker-compose exec backend ping database

# - Python dependency issues
docker-compose build --no-cache backend
```

### Connection Issues

#### Frontend Can't Reach Backend
```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check frontend environment
cat frontend/.env
# Should contain: REACT_APP_API_BASE_URL=http://localhost:8000

# 3. Check CORS configuration
docker-compose logs backend | grep -i cors

# 4. Test from different network
curl -H "Origin: http://localhost:3000" http://localhost:8000/health
```

#### Backend Can't Reach Database
```bash
# 1. Test database connectivity
docker-compose exec backend ping database

# 2. Test database login
docker-compose exec backend mysql -h database -u $DB_USER -p$DB_PASSWORD $DB_NAME

# 3. Check database health
docker-compose exec database mysqladmin ping -h localhost

# 4. Verify network configuration
docker network inspect clash_deck_builder_clash-network
```

### Performance Issues

#### Slow Container Startup
```bash
# 1. Check Docker resource allocation
docker stats

# 2. Increase Docker Desktop resources
# Settings > Resources > Advanced
# Recommended: 4GB RAM, 2 CPUs minimum

# 3. Optimize Docker build
# Add .dockerignore files
echo "node_modules" >> backend/.dockerignore
echo "__pycache__" >> backend/.dockerignore

# 4. Use multi-stage builds for production
```

#### High Resource Usage
```bash
# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check for resource leaks
docker-compose logs backend | grep -i "memory\|leak"

# Limit container resources
# Add to docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 1G
#       cpus: '0.5'
```

#### File Watching Issues (Windows/macOS)
```bash
# Enable polling for file changes
# Add to frontend/.env:
echo "WATCHPACK_POLLING=true" >> frontend/.env
echo "CHOKIDAR_USEPOLLING=true" >> frontend/.env

# Adjust polling interval
echo "CHOKIDAR_INTERVAL=1000" >> frontend/.env
```

### Data Issues

#### Database Data Not Persisting
```bash
# 1. Check volume mount
docker volume inspect clash_deck_builder_mysql_data

# 2. Verify data directory
docker-compose exec database ls -la /var/lib/mysql

# 3. Check for volume conflicts
docker volume ls | grep mysql
```

#### Schema/Migration Issues
```bash
# 1. Check if initialization scripts ran
docker-compose logs database | grep -i "init\|schema"

# 2. Manually run initialization
docker-compose exec database mysql -u root -p$DB_ROOT_PASSWORD $DB_NAME < /docker-entrypoint-initdb.d/01-schema.sql

# 3. Reset database completely
docker-compose down -v
docker-compose up -d database
```

### Security Issues

#### Permission Errors
```bash
# Linux/macOS: Fix file ownership
sudo chown -R $USER:$USER .

# Check Docker group membership
groups $USER | grep docker
# If not in docker group:
sudo usermod -aG docker $USER
# Then logout and login again
```

#### SSL/Certificate Issues
```bash
# For development, disable SSL verification
# Add to backend environment:
PYTHONHTTPSVERIFY=0

# Update certificates in container
docker-compose exec backend apt-get update && apt-get install -y ca-certificates
```

## Diagnostic Tools

### Health Check Script
```bash
#!/bin/bash
# Save as scripts/health-check.sh

echo "=== Docker Environment Health Check ==="

echo "1. Docker Version:"
docker --version
docker-compose --version

echo "2. Container Status:"
docker-compose ps

echo "3. Service Health:"
echo -n "Backend: "
curl -s http://localhost:8000/health > /dev/null && echo "✓ OK" || echo "✗ FAIL"

echo -n "Database: "
docker-compose exec -T database mysqladmin ping -h localhost > /dev/null 2>&1 && echo "✓ OK" || echo "✗ FAIL"

echo "4. Network Connectivity:"
docker-compose exec -T backend ping -c 1 database > /dev/null 2>&1 && echo "Backend → Database: ✓ OK" || echo "Backend → Database: ✗ FAIL"

echo "5. Volume Status:"
docker volume ls | grep clash

echo "6. Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo "7. Recent Errors:"
docker-compose logs --tail=5 backend | grep -i error || echo "No recent backend errors"
docker-compose logs --tail=5 database | grep -i error || echo "No recent database errors"
```

### Log Analysis Script
```bash
#!/bin/bash
# Save as scripts/analyze-logs.sh

echo "=== Log Analysis ==="

echo "Backend Errors:"
docker-compose logs backend | grep -i "error\|exception\|traceback" | tail -10

echo "Database Errors:"
docker-compose logs database | grep -i "error\|warning" | tail -10

echo "Connection Issues:"
docker-compose logs backend | grep -i "connection\|timeout" | tail -5

echo "Performance Issues:"
docker-compose logs backend | grep -i "slow\|timeout\|memory" | tail -5
```

## Recovery Procedures

### Complete Environment Reset
```bash
#!/bin/bash
# Complete reset procedure

echo "Stopping all services..."
docker-compose down

echo "Removing containers and volumes..."
docker-compose down -v
docker system prune -f

echo "Rebuilding containers..."
docker-compose build --no-cache

echo "Starting services..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

echo "Waiting for services to be ready..."
sleep 30

echo "Verifying health..."
curl http://localhost:8000/health
```

### Database Recovery
```bash
#!/bin/bash
# Database recovery procedure

echo "Creating backup of current data..."
./scripts/backup-database.sh

echo "Stopping database..."
docker-compose stop database

echo "Removing database volume..."
docker volume rm clash_deck_builder_mysql_data

echo "Starting fresh database..."
docker-compose up -d database

echo "Waiting for database initialization..."
sleep 60

echo "Restoring data from backup..."
# ./scripts/restore-database.sh [backup-file]

echo "Database recovery complete!"
```

## Best Practices

### Development Workflow
1. Always use `docker-compose down` before `docker-compose up` when changing configuration
2. Use `docker-compose logs -f` to monitor service startup
3. Keep environment files updated and documented
4. Regularly clean up unused Docker resources with `docker system prune`
5. Use health checks to ensure services are ready before connecting

### Performance Optimization
1. Allocate sufficient resources to Docker Desktop
2. Use `.dockerignore` files to exclude unnecessary files
3. Enable file watching polling on Windows/macOS for development
4. Use multi-stage builds for production images
5. Monitor resource usage with `docker stats`

### Security Considerations
1. Never commit `.env` files with real credentials
2. Use strong, unique passwords for each environment
3. Regularly update base images for security patches
4. Limit container resources to prevent resource exhaustion
5. Use secrets management in production environments

### Backup and Recovery
1. Regularly backup database using provided scripts
2. Test backup restoration procedures
3. Keep multiple backup copies with timestamps
4. Document recovery procedures for your team
5. Monitor backup success and storage usage

## Getting Help

### Log Collection for Support
```bash
# Collect comprehensive logs for troubleshooting
mkdir -p debug-logs
docker-compose logs > debug-logs/compose-logs.txt
docker-compose config > debug-logs/compose-config.yml
docker system info > debug-logs/docker-info.txt
docker stats --no-stream > debug-logs/resource-usage.txt
env | grep -E "(DB_|CLASH_|CORS_)" > debug-logs/environment.txt
```

### Common Support Information
When seeking help, please provide:
1. Operating system and Docker version
2. Complete error messages from logs
3. Steps to reproduce the issue
4. Environment configuration (without sensitive data)
5. Output from health check script

### Additional Resources
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MySQL Docker Image Documentation](https://hub.docker.com/_/mysql)
- [Project Development Guide](DEVELOPMENT.md)