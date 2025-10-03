#!/bin/bash

# =============================================================================
# CLASH ROYALE DECK BUILDER - ENVIRONMENT SETUP SCRIPT
# =============================================================================
# This script initializes environment files from the template for consistent
# configuration across different environments.
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

# Function to generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to generate JWT secret
generate_jwt_secret() {
    openssl rand -base64 64 | tr -d "=+/" | cut -c1-64
}

# Function to setup environment file
setup_env_file() {
    local env_file=$1
    local env_type=$2
    
    if [ -f "$env_file" ]; then
        print_warning "$env_file already exists. Skipping creation."
        return 0
    fi
    
    print_status "Creating $env_file for $env_type environment..."
    
    # Copy template
    cp .env.example "$env_file"
    
    # Generate secure passwords
    local db_root_password=$(generate_password)
    local db_user_password=$(generate_password)
    local jwt_secret=$(generate_jwt_secret)
    
    # Update environment-specific values
    case $env_type in
        "local")
            sed -i.bak \
                -e "s/your_secure_root_password_here/local_root_${db_root_password}/" \
                -e "s/your_secure_user_password_here/local_user_${db_user_password}/" \
                -e "s/clash_deck_builder/clash_deck_builder_dev/" \
                -e "s/your_jwt_secret_key_here/${jwt_secret}/" \
                -e "s/DEBUG=false/DEBUG=true/" \
                -e "s/LOG_LEVEL=info/LOG_LEVEL=debug/" \
                -e "s/ENVIRONMENT=production/ENVIRONMENT=development/" \
                -e "s/your_clash_royale_api_key_here/test_api_key_or_mock/" \
                "$env_file"
            ;;
        "docker")
            sed -i.bak \
                -e "s/your_secure_root_password_here/docker_root_${db_root_password}/" \
                -e "s/your_secure_user_password_here/docker_user_${db_user_password}/" \
                -e "s/clash_deck_builder/clash_deck_builder_docker/" \
                -e "s/your_jwt_secret_key_here/${jwt_secret}/" \
                -e "s/DB_HOST=localhost/DB_HOST=database/" \
                -e "s/ENVIRONMENT=production/ENVIRONMENT=docker/" \
                "$env_file"
            ;;
        "production")
            sed -i.bak \
                -e "s/your_secure_root_password_here/prod_root_${db_root_password}/" \
                -e "s/your_secure_user_password_here/prod_user_${db_user_password}/" \
                -e "s/your_jwt_secret_key_here/${jwt_secret}/" \
                "$env_file"
            ;;
    esac
    
    # Remove backup file
    rm -f "${env_file}.bak"
    
    print_success "Created $env_file with secure generated passwords"
}

# Main execution
main() {
    print_status "Starting environment setup for Clash Royale Deck Builder..."
    
    # Check if .env.example exists
    if [ ! -f ".env.example" ]; then
        print_error ".env.example not found! Please ensure you're in the project root directory."
        exit 1
    fi
    
    # Create scripts directory if it doesn't exist
    mkdir -p scripts
    
    # Determine which environment files to create based on arguments
    if [ "$1" = "all" ]; then
        setup_env_file ".env.local" "local"
        setup_env_file ".env.docker" "docker"
        setup_env_file ".env" "production"
    elif [ "$1" = "local" ]; then
        setup_env_file ".env.local" "local"
    elif [ "$1" = "docker" ]; then
        setup_env_file ".env.docker" "docker"
    elif [ "$1" = "production" ]; then
        setup_env_file ".env" "production"
    else
        # Default: create local and docker environments
        setup_env_file ".env.local" "local"
        setup_env_file ".env.docker" "docker"
    fi
    
    print_success "Environment setup completed!"
    echo
    print_warning "IMPORTANT SECURITY REMINDERS:"
    echo "1. Update the Clash Royale API key in your environment files"
    echo "2. For production, use strong, unique passwords"
    echo "3. Never commit .env files to version control"
    echo "4. Rotate passwords and API keys regularly"
    echo
    print_status "Next steps:"
    echo "1. Update CLASH_ROYALE_API_KEY in your environment files"
    echo "2. Review and adjust other configuration values as needed"
    echo "3. Run 'docker-compose up' to start the application"
}

# Show usage if help is requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [environment]"
    echo
    echo "Arguments:"
    echo "  all         Create all environment files (.env.local, .env.docker, .env)"
    echo "  local       Create only .env.local for local development"
    echo "  docker      Create only .env.docker for containerized development"
    echo "  production  Create only .env for production deployment"
    echo "  (no args)   Create .env.local and .env.docker (default)"
    echo
    echo "Examples:"
    echo "  $0              # Create local and docker environments"
    echo "  $0 all          # Create all environment files"
    echo "  $0 production   # Create only production environment"
    exit 0
fi

# Run main function
main "$@"