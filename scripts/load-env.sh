#!/bin/bash
# =============================================================================
# Environment Configuration Loader (Shell Script)
# =============================================================================
# Loads and validates environment variables from centralized configuration files.
# Usage: source scripts/load-env.sh [environment]
# =============================================================================

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_DIR="$PROJECT_ROOT/env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to detect environment
detect_environment() {
    # Check explicit environment variable
    if [[ -n "${ENVIRONMENT:-}" ]]; then
        echo "$ENVIRONMENT"
        return
    fi
    
    # Check for Docker environment
    if [[ -f "/.dockerenv" ]] || [[ -n "${DOCKER_CONTAINER:-}" ]]; then
        echo "docker"
        return
    fi
    
    # Check for production indicators
    if [[ -n "${PRODUCTION:-}" ]] || [[ -n "${PROD:-}" ]] || [[ -n "${RAILWAY_ENVIRONMENT:-}" ]]; then
        echo "production"
        return
    fi
    
    # Default to development
    echo "development"
}

# Function to load environment file
load_env_file() {
    local file_path="$1"
    
    if [[ ! -f "$file_path" ]]; then
        return
    fi
    
    print_info "Loading: $file_path"
    
    # Read file line by line
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Parse key=value pairs
        if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"
            
            # Trim whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            
            # Remove quotes if present
            if [[ "$value" =~ ^\"(.*)\"$ ]] || [[ "$value" =~ ^\'(.*)\'$ ]]; then
                value="${BASH_REMATCH[1]}"
            fi
            
            # Export the variable
            export "$key"="$value"
        fi
    done < "$file_path"
}

# Function to validate environment
validate_environment() {
    local errors=0
    
    print_info "Validating environment configuration..."
    
    # Required variables for all environments
    local required_vars=(
        "DB_HOST" "DB_PORT" "DB_NAME" "DB_USER" "DB_PASSWORD"
        "JWT_SECRET_KEY" "BACKEND_PORT"
    )
    
    # Additional required variables for production
    if [[ "${ENVIRONMENT:-}" == "production" ]]; then
        required_vars+=(
            "GOOGLE_CLIENT_ID" "GOOGLE_CLIENT_SECRET"
            "CLASH_ROYALE_API_KEY"
        )
    fi
    
    # Check required variables
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            print_error "Missing required variable: $var"
            ((errors++))
        fi
    done
    
    # Validate JWT secret length
    if [[ -n "${JWT_SECRET_KEY:-}" ]] && [[ ${#JWT_SECRET_KEY} -lt 32 ]]; then
        print_error "JWT_SECRET_KEY must be at least 32 characters long"
        ((errors++))
    fi
    
    # Validate database port
    if [[ -n "${DB_PORT:-}" ]] && ! [[ "$DB_PORT" =~ ^[0-9]+$ ]] || [[ "$DB_PORT" -lt 1 ]] || [[ "$DB_PORT" -gt 65535 ]]; then
        print_error "DB_PORT must be a valid port number (1-65535)"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        print_success "Environment validation passed"
        return 0
    else
        print_error "Environment validation failed with $errors errors"
        return 1
    fi
}

# Function to show environment summary
show_summary() {
    echo
    print_info "Environment Configuration Summary"
    echo "=================================="
    echo "Environment: ${ENVIRONMENT:-unknown}"
    echo "Database: ${DB_HOST:-unknown}:${DB_PORT:-unknown}/${DB_NAME:-unknown}"
    echo "Backend: ${BACKEND_HOST:-unknown}:${BACKEND_PORT:-unknown}"
    echo "API URL: ${REACT_APP_API_BASE_URL:-unknown}"
    echo "Debug Mode: ${DEBUG:-false}"
    echo "Log Level: ${LOG_LEVEL:-info}"
    echo
}

# Main function
main() {
    local environment="${1:-}"
    local validate_flag="${2:-}"
    
    print_info "Clash Royale Deck Builder - Environment Loader"
    
    # Detect environment if not specified
    if [[ -z "$environment" ]]; then
        environment=$(detect_environment)
        print_info "Auto-detected environment: $environment"
    else
        print_info "Using specified environment: $environment"
    fi
    
    # Set environment variable
    export ENVIRONMENT="$environment"
    
    # Load environment files in order of precedence
    print_info "Loading environment configuration..."
    
    # 1. Load base template (lowest priority)
    load_env_file "$PROJECT_ROOT/.env.template"
    
    # 2. Load environment-specific file
    local env_file="$ENV_DIR/$environment.env"
    if [[ -f "$env_file" ]]; then
        load_env_file "$env_file"
    else
        print_warning "Environment file not found: $env_file"
    fi
    
    # 3. Load local .env file (highest priority)
    load_env_file "$PROJECT_ROOT/.env"
    
    print_success "Environment configuration loaded"
    
    # Validate if requested
    if [[ "$validate_flag" == "--validate" ]] || [[ "$validate_flag" == "-v" ]]; then
        validate_environment
    fi
    
    # Show summary
    show_summary
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
    main "$@"
else
    # Script is being sourced
    main "$@"
fi