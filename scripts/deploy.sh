#!/bin/bash

# =============================================================================
# CLASH ROYALE DECK BUILDER - DEPLOYMENT SCRIPT
# =============================================================================
# This script handles deployment with environment variable validation
# and security best practices.
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to validate required environment variables
validate_env_vars() {
    local env_file=$1
    local missing_vars=()
    
    print_status "Validating environment variables in $env_file..."
    
    # Source the environment file
    if [ -f "$env_file" ]; then
        set -a  # Automatically export all variables
        source "$env_file"
        set +a
    else
        print_error "Environment file $env_file not found!"
        return 1
    fi
    
    # Required variables for all environments
    local required_vars=(
        "DB_ROOT_PASSWORD"
        "DB_NAME"
        "DB_USER"
        "DB_PASSWORD"
        "DB_HOST"
        "DB_PORT"
        "CLASH_ROYALE_API_KEY"
        "DEBUG"
        "LOG_LEVEL"
        "CORS_ORIGINS"
        "ENVIRONMENT"
        "BACKEND_HOST"
        "BACKEND_PORT"
        "JWT_SECRET_KEY"
    )
    
    # Check each required variable
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    # Report missing variables
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    print_success "All required environment variables are set"
    return 0
}

# Function to validate environment variable values
validate_env_values() {
    print_status "Validating environment variable values..."
    
    # Validate database port
    if ! [[ "$DB_PORT" =~ ^[0-9]+$ ]] || [ "$DB_PORT" -lt 1 ] || [ "$DB_PORT" -gt 65535 ]; then
        print_error "DB_PORT must be a valid port number (1-65535)"
        return 1
    fi
    
    # Validate backend port
    if ! [[ "$BACKEND_PORT" =~ ^[0-9]+$ ]] || [ "$BACKEND_PORT" -lt 1 ] || [ "$BACKEND_PORT" -gt 65535 ]; then
        print_error "BACKEND_PORT must be a valid port number (1-65535)"
        return 1
    fi
    
    # Validate debug flag
    if [[ "$DEBUG" != "true" && "$DEBUG" != "false" ]]; then
        print_error "DEBUG must be either 'true' or 'false'"
        return 1
    fi
    
    # Validate log level
    local valid_log_levels=("debug" "info" "warning" "error" "critical")
    if [[ ! " ${valid_log_levels[@]} " =~ " ${LOG_LEVEL} " ]]; then
        print_error "LOG_LEVEL must be one of: ${valid_log_levels[*]}"
        return 1
    fi
    
    # Validate environment type
    local valid_environments=("development" "docker" "production")
    if [[ ! " ${valid_environments[@]} " =~ " ${ENVIRONMENT} " ]]; then
        print_error "ENVIRONMENT must be one of: ${valid_environments[*]}"
        return 1
    fi
    
    # Security checks for production
    if [ "$ENVIRONMENT" = "production" ]; then
        print_status "Performing additional security checks for production..."
        
        # Check for default/weak passwords
        local weak_patterns=("password" "123" "test" "default" "admin" "root")
        for pattern in "${weak_patterns[@]}"; do
            if [[ "$DB_ROOT_PASSWORD" == *"$pattern"* ]] || [[ "$DB_PASSWORD" == *"$pattern"* ]]; then
                print_error "Production passwords should not contain common patterns like '$pattern'"
                return 1
            fi
        done
        
        # Check password length
        if [ ${#DB_ROOT_PASSWORD} -lt 12 ] || [ ${#DB_PASSWORD} -lt 12 ]; then
            print_error "Production passwords should be at least 12 characters long"
            return 1
        fi
        
        # Check for test API key
        if [[ "$CLASH_ROYALE_API_KEY" == *"test"* ]] || [[ "$CLASH_ROYALE_API_KEY" == *"mock"* ]]; then
            print_error "Production environment requires a real Clash Royale API key"
            return 1
        fi
        
        # Check JWT secret strength
        if [ ${#JWT_SECRET_KEY} -lt 32 ]; then
            print_error "Production JWT secret should be at least 32 characters long"
            return 1
        fi
        
        print_success "Production security checks passed"
    fi
    
    print_success "Environment variable values are valid"
    return 0
}

# Function to check Docker availability
check_docker() {
    print_status "Checking Docker availability..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        return 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        return 1
    fi
    
    print_success "Docker and Docker Compose are available"
    return 0
}

# Function to deploy to specific environment
deploy_environment() {
    local environment=$1
    local compose_files=""
    local env_file=""
    
    print_status "Deploying to $environment environment..."
    
    # Determine compose files and environment file based on environment
    case $environment in
        "development"|"local")
            compose_files="-f docker-compose.yml -f docker-compose.dev.yml"
            env_file=".env.local"
            ;;
        "docker")
            compose_files="-f docker-compose.yml -f docker-compose.dev.yml"
            env_file=".env.docker"
            ;;
        "production")
            compose_files="-f docker-compose.yml -f docker-compose.prod.yml"
            env_file=".env"
            ;;
        *)
            print_error "Unknown environment: $environment"
            print_error "Valid environments: development, docker, production"
            return 1
            ;;
    esac
    
    # Validate environment variables
    if ! validate_env_vars "$env_file"; then
        return 1
    fi
    
    if ! validate_env_values; then
        return 1
    fi
    
    # Check Docker availability
    if ! check_docker; then
        return 1
    fi
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose $compose_files down --remove-orphans || true
    
    # Pull latest images
    print_status "Pulling latest images..."
    docker-compose $compose_files pull
    
    # Build and start containers
    print_status "Building and starting containers..."
    docker-compose $compose_files up -d --build
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose $compose_files ps | grep -q "Up (healthy)"; then
            print_success "Services are healthy!"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Services failed to become healthy within timeout"
            docker-compose $compose_files logs
            return 1
        fi
        
        print_status "Attempt $attempt/$max_attempts - waiting for services..."
        sleep 10
        ((attempt++))
    done
    
    # Show running services
    print_status "Running services:"
    docker-compose $compose_files ps
    
    print_success "Deployment to $environment completed successfully!"
    
    # Show access information
    echo
    print_status "Access Information:"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Health Check: http://localhost:8000/health"
    echo
    print_status "Useful Commands:"
    echo "  View logs: docker-compose $compose_files logs -f"
    echo "  Stop services: docker-compose $compose_files down"
    echo "  Restart services: docker-compose $compose_files restart"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [ENVIRONMENT] [OPTIONS]"
    echo
    echo "ENVIRONMENT:"
    echo "  development  Deploy for local development (uses .env.local)"
    echo "  docker       Deploy for containerized development (uses .env.docker)"
    echo "  production   Deploy for production (uses .env)"
    echo
    echo "OPTIONS:"
    echo "  --validate-only  Only validate environment variables, don't deploy"
    echo "  --help, -h       Show this help message"
    echo
    echo "Examples:"
    echo "  $0 development           # Deploy for local development"
    echo "  $0 docker               # Deploy for containerized development"
    echo "  $0 production           # Deploy for production"
    echo "  $0 production --validate-only  # Only validate production environment"
}

# Main execution
main() {
    local environment=${1:-development}
    local validate_only=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --validate-only)
                validate_only=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            development|docker|production)
                environment=$1
                shift
                ;;
            *)
                print_error "Unknown argument: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    print_status "Starting deployment script for Clash Royale Deck Builder..."
    print_status "Target environment: $environment"
    
    if [ "$validate_only" = true ]; then
        print_status "Validation-only mode enabled"
        
        # Determine environment file
        local env_file=""
        case $environment in
            "development"|"local") env_file=".env.local" ;;
            "docker") env_file=".env.docker" ;;
            "production") env_file=".env" ;;
        esac
        
        # Validate environment variables
        if validate_env_vars "$env_file" && validate_env_values; then
            print_success "Environment validation passed!"
            exit 0
        else
            print_error "Environment validation failed!"
            exit 1
        fi
    else
        # Full deployment
        if deploy_environment "$environment"; then
            print_success "Deployment completed successfully!"
            exit 0
        else
            print_error "Deployment failed!"
            exit 1
        fi
    fi
}

# Run main function with all arguments
main "$@"