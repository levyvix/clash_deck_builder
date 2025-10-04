# Environment Variables Setup Guide

## Overview

This project uses a centralized environment configuration system that eliminates duplication and provides a single source of truth for all environment variables across backend, frontend, and Docker configurations.

## Quick Start

### 1. Copy the Environment Template
```bash
# Copy the main template to create your local environment
cp .env.template .env

# Edit with your actual values
nano .env  # or use your preferred editor
```

### 2. Load Environment (Optional)
```bash
# Load environment variables into your shell
source scripts/load-env.sh

# Or validate your configuration
source scripts/load-env.sh development --validate
```

### 3. Start Development
```bash
# Backend
cd backend
uv install
uv run uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm start
```

## Environment Structure

### Centralized Files
- `.env.template` - Master template with all variables and documentation
- `env/development.env` - Development-specific overrides
- `env/docker.env` - Docker-specific overrides  
- `env/production.env.example` - Production template (copy to `production.env`)

### Local Files (Git-ignored)
- `.env` - Your local environment (highest priority)
- `env/production.env` - Production secrets (never commit!)

## Variable Categories

### Database Configuration
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=clash_deck_builder
DB_USER=clash_user
DB_PASSWORD=your_secure_password
DB_ROOT_PASSWORD=your_root_password
```

### Authentication & Security
```bash
# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# JWT Configuration
JWT_SECRET_KEY=your_32_character_minimum_secret_key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### External APIs
```bash
# Clash Royale API (get from https://developer.clashroyale.com/)
CLASH_ROYALE_API_KEY=your_api_key_here
```

### Application Settings
```bash
# Environment type
ENVIRONMENT=development  # development, docker, production

# Server configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=3000

# API connection
REACT_APP_API_BASE_URL=http://localhost:8000

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Debug settings
DEBUG=true
LOG_LEVEL=debug
```

## Environment-Specific Setup

### Development Environment
```bash
# Use development defaults
source scripts/load-env.sh development

# Or manually set
export ENVIRONMENT=development
```

**Characteristics:**
- Debug mode enabled
- Verbose logging
- Relaxed security settings
- Local database connection
- Extended timeouts for debugging

### Docker Environment
```bash
# Use Docker configuration
source scripts/load-env.sh docker

# Or manually set
export ENVIRONMENT=docker
```

**Characteristics:**
- Container-optimized settings
- Service name resolution (database, backend)
- Production-like security
- Container networking support

### Production Environment
```bash
# Create production config (never commit this file!)
cp env/production.env.example env/production.env
# Edit with actual production values

# Load production environment
source scripts/load-env.sh production
```

**Characteristics:**
- Security hardened
- Minimal logging
- Strict validation
- External service connections
- Performance optimized

## Google OAuth Setup

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create or select a project**
3. **Enable APIs**:
   - Google Identity Services API
4. **Configure OAuth Consent Screen**:
   - User Type: External
   - Add your domain to authorized domains
5. **Create OAuth 2.0 Client ID**:
   - Application type: Web application
   - Authorized JavaScript origins:
     - `http://localhost:3000` (development)
     - `http://localhost:8000` (backend)
     - Your production domain
   - Authorized redirect URIs:
     - `http://localhost:3000/auth/callback`
     - Your production callback URL
6. **Copy credentials to environment**:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   ```

## Clash Royale API Setup

1. **Visit**: https://developer.clashroyale.com/
2. **Create an account** and verify email
3. **Create a new API key**:
   - Name: Clash Deck Builder
   - Description: Deck building application
   - IP Address: Your development IP (or 0.0.0.0 for testing)
4. **Copy the API key**:
   ```bash
   CLASH_ROYALE_API_KEY=your_generated_api_key_here
   ```

## Database Setup

### Local MySQL
```bash
# Install MySQL (Ubuntu/Debian)
sudo apt update
sudo apt install mysql-server

# Install MySQL (macOS with Homebrew)
brew install mysql
brew services start mysql

# Create database and user
mysql -u root -p
CREATE DATABASE clash_deck_builder_dev;
CREATE USER 'clash_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON clash_deck_builder_dev.* TO 'clash_user'@'localhost';
FLUSH PRIVILEGES;
```

### Docker MySQL
```bash
# Start with Docker Compose
docker-compose up database

# Or run standalone
docker run -d \
  --name clash-mysql \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_DATABASE=clash_deck_builder \
  -e MYSQL_USER=clash_user \
  -e MYSQL_PASSWORD=user_password \
  -p 3306:3306 \
  mysql:8.0
```

## Validation & Troubleshooting

### Validate Configuration
```bash
# Validate current environment
python scripts/load-env.py --validate

# Or with shell script
source scripts/load-env.sh development --validate
```

### Common Issues

**1. Missing Required Variables**
```bash
❌ Missing required variable: GOOGLE_CLIENT_ID
```
**Solution**: Add the missing variable to your `.env` file

**2. JWT Secret Too Short**
```bash
❌ JWT_SECRET_KEY must be at least 32 characters long
```
**Solution**: Generate a longer secret:
```bash
# Generate secure JWT secret
openssl rand -base64 32
```

**3. Database Connection Failed**
```bash
❌ Cannot connect to database
```
**Solution**: Check database settings and ensure MySQL is running:
```bash
# Check MySQL status
sudo systemctl status mysql

# Test connection
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME
```

**4. CORS Errors**
```bash
❌ CORS policy blocked request
```
**Solution**: Update CORS_ORIGINS to include your frontend URL:
```bash
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Debug Configuration
```bash
# Show current configuration
source scripts/load-env.sh development

# Export configuration to file for inspection
python scripts/load-env.py --export debug-config.env

# Check what the backend sees
cd backend
uv run python -c "from src.utils.config import settings; print(settings.dict())"
```

## Migration from Old Structure

If you're migrating from the old scattered environment files:

### 1. Backup Existing Files
```bash
mkdir env-backup
cp .env* env-backup/
cp backend/.env* env-backup/
cp frontend/.env* env-backup/
```

### 2. Extract Your Values
```bash
# Create your new .env from template
cp .env.template .env

# Copy your actual values from backup files
# Focus on these key variables:
# - Database credentials
# - Google OAuth credentials  
# - Clash Royale API key
# - Any custom settings
```

### 3. Clean Up Old Files
```bash
# Remove old scattered files (after confirming new setup works)
rm backend/.env backend/.env.example
rm frontend/.env.local frontend/.env.docker
# Keep frontend/.env and frontend/.env.example for now (they'll be updated)
```

### 4. Test New Configuration
```bash
# Validate new setup
source scripts/load-env.sh --validate

# Test backend
cd backend && uv run uvicorn main:app --reload

# Test frontend  
cd frontend && npm start
```

## Security Best Practices

1. **Never commit sensitive files**:
   - `.env` (local environment)
   - `env/production.env` (production secrets)

2. **Use strong secrets**:
   ```bash
   # Generate secure passwords
   openssl rand -base64 32
   
   # Generate JWT secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Rotate credentials regularly**:
   - JWT secrets
   - Database passwords
   - API keys

4. **Use environment-specific values**:
   - Different database names per environment
   - Different JWT secrets per environment
   - Appropriate debug/logging levels

5. **Validate in CI/CD**:
   ```bash
   # Add to your CI pipeline
   python scripts/load-env.py --environment production --validate
   ```

## Advanced Usage

### Custom Environment Files
```bash
# Create custom environment for testing
cp env/development.env env/testing.env
# Edit testing-specific values

# Load custom environment
source scripts/load-env.sh testing
```

### Environment Variable Precedence
1. **Actual environment variables** (highest priority)
2. **Local `.env` file**
3. **Environment-specific file** (`env/{environment}.env`)
4. **Base template** (`.env.template`, lowest priority)

### Docker Compose Integration
```yaml
# docker-compose.yml
services:
  backend:
    env_file:
      - .env
      - env/docker.env
    environment:
      - ENVIRONMENT=docker
```

This centralized approach provides better maintainability, security, and consistency across all parts of your application.