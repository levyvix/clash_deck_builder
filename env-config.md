# Environment Variables Centralization Plan

## Current State Analysis

The project currently has environment variables scattered across multiple files:

### Root Level
- `.env` - Docker Compose variables (DB, API keys, CORS)
- `.env.example` - Comprehensive template with all variables
- `.env.local` - Local development defaults
- `.env.docker` - Docker development configuration
- `.env.docker.example` - Docker template

### Backend
- `backend/.env` - Backend-specific variables (DB, OAuth, JWT)
- `backend/.env.example` - Backend template

### Frontend
- `frontend/.env` - Frontend variables (API URL, Google Client ID)
- `frontend/.env.example` - Frontend template
- `frontend/.env.local` - Frontend local development
- `frontend/.env.docker` - Frontend Docker configuration

## Issues Identified

1. **Duplication**: Same variables defined in multiple places
2. **Inconsistency**: Different values for same variables across files
3. **Maintenance**: Hard to keep all files in sync
4. **Security**: Sensitive values scattered across multiple files

## Proposed Solution

### 1. Centralized Environment Structure
```
├── .env                    # Main environment file (gitignored)
├── .env.example           # Complete template for all environments
├── .env.development       # Development-specific overrides
├── .env.docker           # Docker-specific overrides
├── .env.production       # Production-specific overrides (gitignored)
└── env/                  # Environment configuration directory
    ├── shared.env        # Shared variables across all environments
    ├── development.env   # Development-specific variables
    ├── docker.env        # Docker-specific variables
    └── production.env    # Production-specific variables (gitignored)
```

### 2. Variable Categories
- **Database**: Connection settings, credentials
- **Authentication**: Google OAuth, JWT configuration
- **External APIs**: Clash Royale API keys
- **Application**: Debug, logging, CORS settings
- **Infrastructure**: Ports, hosts, timeouts

### 3. Implementation Steps
1. Create centralized environment files
2. Update backend config to load from centralized location
3. Update frontend config to use centralized variables
4. Update Docker Compose to use centralized files
5. Create environment validation scripts
6. Update documentation and setup guides

This will provide a single source of truth for all environment configuration while maintaining flexibility for different deployment scenarios.