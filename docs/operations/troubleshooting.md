# Troubleshooting Guide

Common issues and their solutions when working with the Clash Royale Deck Builder.

## Quick Diagnostics

Run these commands to quickly diagnose issues:

```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# View backend logs
docker-compose logs -f backend

# View database logs
docker-compose logs -f database

# Check environment configuration
cd backend
uv run python -c "from src.utils.config import settings; print(settings.dict())"
```

## Backend Issues

### Backend Won't Start

**Symptoms:**
- Backend container exits immediately
- Error: "Cannot connect to database"
- Error: "Address already in use"

**Solutions:**

1. **Check database is running:**
```bash
docker-compose ps
# Should show database as "Up"

# If not, start it:
docker-compose up -d database

# Wait 10 seconds for MySQL to initialize
sleep 10
```

2. **Verify environment variables:**
```bash
cd backend
cat .env | grep DB_

# Should show:
# DB_HOST=database  (for Docker) or localhost (for local)
# DB_PORT=3306
# DB_NAME=clash_deck_builder
# DB_USER=clash_user
# DB_PASSWORD=<your_password>
```

3. **Check port 8000 is available:**
```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000

# If port is in use, kill the process or change BACKEND_PORT
```

4. **View detailed error logs:**
```bash
docker-compose logs backend | tail -50

# Or run backend directly to see errors
cd backend
uv run uvicorn src.main:app --reload
```

5. **Database connection test:**
```bash
docker-compose exec database mysql -u clash_user -p clash_deck_builder

# If this fails, database isn't ready or credentials are wrong
```

### Missing Dependencies

**Symptoms:**
- ImportError or ModuleNotFoundError
- Error: "No module named 'fastapi'"

**Solutions:**

```bash
cd backend

# Ensure UV is installed
uv --version

# Install/update dependencies
uv sync

# If still failing, clean and reinstall
rm -rf .venv
uv sync

# Check installed packages
uv pip list
```

### Database Migration Errors

**Symptoms:**
- Error: "Table already exists"
- Error: "Unknown column"
- Migrations won't run

**Solutions:**

1. **Check migration status:**
```bash
cd database/migrations

# View migration logs
cat logs/*.log | tail -50

# Check applied migrations in database
docker-compose exec database mysql -u root -p -e "USE clash_deck_builder; SELECT * FROM schema_migrations;"
```

2. **Reset database (CAUTION: destroys data):**
```bash
# Stop all services
docker-compose down -v

# Start fresh
docker-compose up -d database

# Wait for MySQL to initialize
sleep 10

# Reinitialize schema
docker-compose exec database mysql -u clash_user -p clash_deck_builder < database/init/01-schema.sql
```

3. **Manual migration:**
```bash
# Connect to database
docker-compose exec database mysql -u root -p clash_deck_builder

# Run SQL manually
SOURCE /path/to/migration.sql;
```

### API Errors

**Symptom: 500 Internal Server Error**

```bash
# Check backend logs for stack trace
docker-compose logs backend | grep -A 20 "ERROR"

# Common causes:
# 1. Database connection lost
# 2. Missing environment variables
# 3. Invalid data format
# 4. Uncaught exception in code
```

**Symptom: 401 Unauthorized**

```bash
# JWT token issues
# - Token expired (access tokens last 15 minutes)
# - Invalid token
# - Missing Authorization header

# Check token expiration
# Frontend should automatically refresh using refresh token

# Check backend JWT configuration
echo $JWT_SECRET_KEY  # Should be set and at least 32 chars
```

**Symptom: 422 Unprocessable Entity**

```bash
# Request validation failed
# Check request payload matches Pydantic model

# View detailed validation error in response body
# Example: Missing required field, wrong type, etc.
```

## Frontend Issues

### Frontend Won't Start

**Symptoms:**
- Error: "PORT 3000 is already in use"
- Error: "Module not found"
- Build fails

**Solutions:**

1. **Port already in use:**
```bash
# Find process using port 3000
lsof -i :3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process or use different port
PORT=3001 npm start
```

2. **Missing dependencies:**
```bash
cd frontend

# Clear and reinstall
rm -rf node_modules package-lock.json
npm install

# If still failing, clear npm cache
npm cache clean --force
npm install
```

3. **TypeScript errors:**
```bash
# Check for TypeScript errors
npm run build

# If errors, fix them or (temporarily) disable strict mode
# in tsconfig.json: "strict": false
```

### Frontend Can't Connect to Backend

**Symptoms:**
- Network errors in console
- "Failed to fetch" errors
- CORS errors

**Solutions:**

1. **Verify backend is running:**
```bash
# Test backend health
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

2. **Check REACT_APP_API_BASE_URL:**
```bash
cd frontend

# Should be set in .env
cat .env | grep REACT_APP_API_BASE_URL

# Should be: http://localhost:8000

# If not set:
echo "REACT_APP_API_BASE_URL=http://localhost:8000" >> .env

# Restart frontend
npm start
```

3. **CORS errors:**
```bash
# Check backend CORS configuration
cd backend
cat src/main.py | grep -A 5 "CORSMiddleware"

# Ensure CORS_ORIGINS includes frontend URL
echo $CORS_ORIGINS
# Should include: http://localhost:3000

# Update .env if needed
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

4. **Clear browser cache:**
```bash
# Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

# Or clear site data:
# Chrome DevTools → Application → Clear storage
```

### Google OAuth Not Working

**Symptoms:**
- "Invalid client" error
- OAuth popup doesn't appear
- Authentication fails

**Solutions:**

1. **Verify Google Client ID:**
```bash
# Check frontend env
cd frontend
grep REACT_APP_GOOGLE_CLIENT_ID .env

# Should end with: .apps.googleusercontent.com
```

2. **Check authorized origins:**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Navigate to: APIs & Services → Credentials
- Edit OAuth 2.0 Client ID
- Ensure authorized JavaScript origins include:
  - `http://localhost:3000`
  - `http://localhost:8000`

3. **Check authorized redirect URIs:**
- Should include: `http://localhost:3000/auth/callback`

4. **Clear OAuth state:**
```bash
# Clear localStorage in browser console
localStorage.clear()

# Or specific keys
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')
```

## Database Issues

### Can't Connect to Database

**Symptoms:**
- Error: "Can't connect to MySQL server"
- Connection timeout
- Access denied

**Solutions:**

1. **Check database is running:**
```bash
docker-compose ps database

# Should show "Up"
# If not:
docker-compose up -d database
docker-compose logs -f database
```

2. **Test connection:**
```bash
# From host
mysql -h localhost -P 3306 -u clash_user -p clash_deck_builder

# From Docker network
docker-compose exec database mysql -u clash_user -p clash_deck_builder

# If "Access denied", check credentials in .env
```

3. **Reset database password:**
```bash
# Connect as root
docker-compose exec database mysql -u root -p

# Run in MySQL:
ALTER USER 'clash_user'@'%' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;

# Update .env with new password
```

### Database Container Won't Start

**Symptoms:**
- Database container exits immediately
- Error: "Can't start server"

**Solutions:**

```bash
# View logs
docker-compose logs database

# Common causes:
# 1. Port 3306 already in use
sudo lsof -i :3306  # Find process
# Kill it or change DB_PORT

# 2. Corrupted volume
docker-compose down -v  # WARNING: Deletes data
docker-compose up -d database

# 3. Insufficient disk space
df -h  # Check available space
```

### Slow Queries

**Symptoms:**
- API requests take > 1 second
- Database CPU high

**Solutions:**

```bash
# Enable slow query log
# Add to docker-compose.yml database service:
command: --slow-query-log --long-query-time=1

# View slow queries
docker-compose exec database mysql -u root -p
SHOW FULL PROCESSLIST;

# Check for missing indexes
USE clash_deck_builder;
EXPLAIN SELECT * FROM decks WHERE user_id = 1;

# Add indexes if needed
# See database/init/02-indexes.sql
```

## Docker Issues

### Docker Compose Fails

**Symptoms:**
- Error: "no configuration file provided"
- Services won't start
- Volume mount errors

**Solutions:**

```bash
# Verify docker-compose.yml exists
ls -la docker-compose.yml

# Check Docker is running
docker ps

# Check file permissions
chmod 644 docker-compose.yml

# Validate compose file
docker-compose config

# Check Docker disk space
docker system df
docker system prune  # Clean up if needed
```

### Container Keeps Restarting

**Symptoms:**
- Container status shows "Restarting"
- Service not accessible

**Solutions:**

```bash
# View logs to see why it's crashing
docker-compose logs -f <service-name>

# Check exit code
docker-compose ps

# Common causes:
# 1. Missing environment variables
# 2. Port conflict
# 3. Dependency not ready (database)
# 4. Application crash on startup

# Disable restart to see error
# In docker-compose.yml, remove: restart: always
```

## Testing Issues

### Tests Failing

**Backend tests:**
```bash
cd backend

# Clear test cache
uv run pytest --cache-clear

# Run with verbose output
uv run pytest -v tests/unit/test_card_service.py

# Check test database
# Ensure TEST_DB_NAME is set in .env

# View test logs
uv run pytest --log-cli-level=DEBUG
```

**Frontend tests:**
```bash
cd frontend

# Clear Jest cache
npm test -- --clearCache

# Run with verbose output
npm test -- --verbose

# Run specific test
npm test -- DeckBuilder.test.tsx

# Update snapshots if needed
npm test -- -u
```

### Test Database Issues

**Symptoms:**
- Tests fail with database errors
- Can't create test database

**Solutions:**

```bash
# Create dedicated test database
docker-compose exec database mysql -u root -p

CREATE DATABASE clash_deck_builder_test;
GRANT ALL PRIVILEGES ON clash_deck_builder_test.* TO 'clash_user'@'%';
FLUSH PRIVILEGES;

# Update test configuration
# backend/tests/conftest.py should use TEST_DB_NAME

# Run migrations on test database
# In tests/conftest.py, ensure migrations run before tests
```

## Performance Issues

### Slow Page Load

**Check:**
1. **Network tab** in browser DevTools
2. **Backend response times** in logs
3. **Database query performance**
4. **Bundle size** (frontend)

**Solutions:**

```bash
# Backend profiling
# Add logging to measure endpoint times

# Frontend bundle analysis
cd frontend
npm run build
# Check build output for bundle sizes

# Database optimization
# Add indexes for frequently queried columns
# Use EXPLAIN to analyze query plans

# Enable caching
# Add Redis for frequently accessed data (future)
```

### High Memory Usage

**Check:**
```bash
# Docker stats
docker stats

# Backend memory
docker-compose exec backend top

# Database memory
docker-compose exec database top
```

**Solutions:**
- Reduce `max_connections` in MySQL
- Add pagination to API endpoints
- Limit result sets
- Review connection pooling settings

## Getting Help

If you're still stuck:

1. **Check logs** - Most issues show up in logs
2. **Search issues** - GitHub/GitLab issue tracker
3. **Review docs** - [Architecture](../architecture/overview.md), [API](../api/overview.md)
4. **Ask the team** - Slack/Discord/Email

## Useful Commands Reference

```bash
# Health checks
curl http://localhost:8000/health
docker-compose ps
docker stats

# Logs
docker-compose logs -f backend
docker-compose logs -f database
docker-compose logs --tail=100

# Database
docker-compose exec database mysql -u clash_user -p clash_deck_builder
docker-compose exec database mysqldump -u root -p clash_deck_builder > backup.sql

# Cleanup
docker-compose down
docker-compose down -v  # Include volumes
docker system prune  # Clean up Docker

# Reset everything
docker-compose down -v
rm -rf backend/.venv
rm -rf frontend/node_modules
# Then start fresh

# Environment debug
env | grep -E '(DB_|GOOGLE_|CLASH_|JWT_|REACT_)'
source scripts/load-env.sh development --validate
```
