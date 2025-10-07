# Environment Setup

Complete guide to configuring your development environment for the Clash Royale Deck Builder.

## Environment Files Overview

The project uses a centralized environment configuration system:

- **`.env.template`** - Master template with all variables and documentation
- **`.env`** - Your local environment (git-ignored, highest priority)
- **`env/development.env`** - Development-specific overrides
- **`env/docker.env`** - Docker-specific overrides
- **`env/production.env`** - Production secrets (git-ignored, create from `.example`)

## Quick Setup

```bash
# 1. Copy the environment template
cp .env.template .env

# 2. Edit with your actual values
nano .env

# 3. Validate configuration (optional)
source scripts/load-env.sh development --validate
```

## Required Environment Variables

### Database Configuration

```bash
DB_HOST=localhost           # Use 'database' in Docker environment
DB_PORT=3306
DB_NAME=clash_deck_builder
DB_USER=clash_user
DB_PASSWORD=your_secure_password
DB_ROOT_PASSWORD=root_password
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable **Google Identity Services API**
4. Configure OAuth Consent Screen:
   - User Type: External
   - Add authorized domains
5. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized JavaScript origins:
     - `http://localhost:3000` (development)
     - `http://localhost:8000` (backend)
     - Your production domain
   - Authorized redirect URIs:
     - `http://localhost:3000/auth/callback`
     - Your production callback URL
6. Add credentials to `.env`:

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### Clash Royale API Setup

1. Visit [Clash Royale Developer Portal](https://developer.clashroyale.com/)
2. Create an account and verify email
3. Create a new API key:
   - Name: Clash Deck Builder
   - Description: Deck building application
   - IP Address: Your development IP (or `0.0.0.0` for testing)
4. Add to `.env`:

```bash
CLASH_ROYALE_API_KEY=your_generated_api_key_here
```

### JWT Configuration

```bash
JWT_SECRET_KEY=your_32_character_minimum_secret_key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

Generate a secure JWT secret:
```bash
openssl rand -base64 32
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

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Debug settings
DEBUG=true
LOG_LEVEL=debug  # debug, info, warning, error
```

## Environment-Specific Configuration

### Development Environment

```bash
# Load development configuration
source scripts/load-env.sh development
```

**Characteristics:**
- Debug mode enabled
- Verbose logging
- Relaxed security settings
- Local database connection
- Extended timeouts for debugging

### Docker Environment

```bash
# Load Docker configuration
source scripts/load-env.sh docker
```

**Key differences:**
```bash
DB_HOST=database              # Use container name
ENVIRONMENT=docker
REACT_APP_API_BASE_URL=http://backend:8000
```

**Characteristics:**
- Container-optimized settings
- Service name resolution (database, backend)
- Production-like security
- Container networking support

### Production Environment

```bash
# Create production config (never commit!)
cp env/production.env.example env/production.env

# Edit with production values
nano env/production.env

# Load production environment
source scripts/load-env.sh production
```

**Characteristics:**
- Security hardened
- Minimal logging
- Strict validation
- External service connections
- Performance optimized

## Database Setup

### Using Docker (Recommended)

```bash
# Start database container
docker-compose up -d database

# Verify it's running
docker-compose ps

# Connect to database
docker-compose exec database mysql -u clash_user -p clash_deck_builder
```

### Local MySQL Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

**Create Database:**
```bash
mysql -u root -p

CREATE DATABASE clash_deck_builder;
CREATE USER 'clash_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON clash_deck_builder.* TO 'clash_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Validation & Troubleshooting

### Validate Configuration

```bash
# Validate environment
python scripts/load-env.py --validate

# Or with shell script
source scripts/load-env.sh development --validate
```

### Common Issues

#### Missing Required Variables

**Error:**
```
❌ Missing required variable: GOOGLE_CLIENT_ID
```

**Solution:**
Add the missing variable to your `.env` file

#### JWT Secret Too Short

**Error:**
```
❌ JWT_SECRET_KEY must be at least 32 characters long
```

**Solution:**
```bash
# Generate a secure JWT secret
openssl rand -base64 32

# Or with Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Database Connection Failed

**Error:**
```
❌ Cannot connect to database
```

**Solutions:**
```bash
# Check MySQL status
sudo systemctl status mysql

# For Docker
docker-compose ps
docker-compose logs database

# Test connection
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME
```

#### CORS Errors

**Error:**
```
❌ CORS policy blocked request from origin
```

**Solution:**
Update `CORS_ORIGINS` in `.env`:
```bash
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000
```

### Debug Configuration

```bash
# Show current configuration
source scripts/load-env.sh development

# Check what backend sees
cd backend
uv run python -c "from src.utils.config import settings; import json; print(json.dumps(settings.dict(), indent=2))"

# Export configuration for inspection
python scripts/load-env.py --export debug-config.env
```

## Security Best Practices

### 1. Never Commit Sensitive Files

Files in `.gitignore`:
- `.env` (local environment)
- `env/production.env` (production secrets)
- Any file containing actual credentials

### 2. Use Strong Secrets

```bash
# Generate secure passwords
openssl rand -base64 32

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate UUID for tracking
python -c "import uuid; print(uuid.uuid4())"
```

### 3. Rotate Credentials Regularly

- JWT secrets (every 90 days)
- Database passwords (every 90 days)
- API keys (as recommended by provider)
- OAuth client secrets (yearly)

### 4. Use Environment-Specific Values

- Different database names per environment
- Different JWT secrets per environment
- Appropriate debug/logging levels per environment
- Different API keys for dev/prod

### 5. Validate in CI/CD

```bash
# Add to your CI pipeline
python scripts/load-env.py --environment production --validate --strict
```

## Advanced Usage

### Custom Environment Files

```bash
# Create custom environment for testing
cp env/development.env env/testing.env

# Edit testing-specific values
nano env/testing.env

# Load custom environment
source scripts/load-env.sh testing
```

### Environment Variable Precedence

Priority order (highest to lowest):

1. **Actual environment variables** (exported in shell)
2. **Local `.env` file**
3. **Environment-specific file** (`env/{environment}.env`)
4. **Base template** (`.env.template`)

### Docker Compose Integration

The Docker Compose file loads environment variables automatically:

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

## Next Steps

- Complete the [Quick Start Guide](quickstart.md) to run the application
- Learn about [Development Workflow](workflow.md)
- Review [Backend Development](../development/backend.md) practices
- Explore the [Architecture](../architecture/overview.md)
