# Docker Setup Guide

This document explains how to run the Clash Royale Deck Builder using Docker containers.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

### Development Environment

1. **Start the development stack:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the stack:**
   ```bash
   docker-compose down
   ```

### Production Environment

1. **Ensure you have a production .env file with secure values**
2. **Start the production stack:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## Environment Files

- `.env.local` - Local development configuration
- `.env.docker` - Docker development configuration  
- `.env` - Production configuration (create from .env.example)

## Services

### Database (MySQL 8.0)
- **Container:** `clash-db`
- **Port:** 3306 (exposed in development only)
- **Data:** Persisted in `mysql_data` Docker volume
- **Initialization:** Automatic schema and seed data setup

### Backend (FastAPI)
- **Container:** `clash-backend`
- **Port:** 8000
- **Health Check:** `http://localhost:8000/health`
- **Hot Reload:** Enabled in development mode

## Useful Commands

### View running containers
```bash
docker-compose ps
```

### Access database directly
```bash
docker-compose exec database mysql -u clash_user -p clash_deck_builder_docker
```

### View backend logs
```bash
docker-compose logs backend
```

### Rebuild containers
```bash
docker-compose build --no-cache
```

### Clean up everything
```bash
docker-compose down -v --remove-orphans
docker system prune -f
```

## Troubleshooting

### Database connection issues
1. Check if database container is healthy: `docker-compose ps`
2. View database logs: `docker-compose logs database`
3. Verify environment variables are set correctly

### Backend startup issues
1. Check backend logs: `docker-compose logs backend`
2. Ensure database is ready before backend starts
3. Verify UV dependencies are installed correctly

### Port conflicts
- Change ports in docker-compose.yml if 3306 or 8000 are already in use
- Update CORS_ORIGINS if using different ports

## Development Workflow

1. **Start containers:** `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d`
2. **Make code changes** - Backend will auto-reload
3. **View changes** at `http://localhost:8000`
4. **Stop when done:** `docker-compose down`

## Data Persistence

- Database data is stored in the `mysql_data` Docker volume
- Backups can be stored in `./database/backups/` directory
- To reset database: `docker-compose down -v` (removes all data)