#!/bin/bash

# Docker Backup Integration Script
# Integrates backup functionality with Docker Compose volumes and services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  backup                 Create a database backup"
    echo "  restore FILE           Restore database from backup file"
    echo "  list                   List available backups"
    echo "  cleanup DAYS           Clean up backups older than DAYS"
    echo "  setup                  Set up backup directory and permissions"
    echo ""
    echo "Options:"
    echo "  -e, --env ENV          Environment (dev, docker, prod)"
    echo "  -f, --force           Force operation without confirmation"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 backup                              # Create backup with defaults"
    echo "  $0 backup -e dev                       # Create backup for dev environment"
    echo "  $0 restore backup.sql.gz               # Restore from backup"
    echo "  $0 list                                # List available backups"
    echo "  $0 cleanup 7                           # Remove backups older than 7 days"
}

# Function to determine Docker Compose configuration
get_compose_config() {
    local env="$1"
    local compose_files="-f docker-compose.yml"
    
    case "$env" in
        "dev"|"development")
            if [ -f "$PROJECT_ROOT/docker-compose.dev.yml" ]; then
                compose_files="$compose_files -f docker-compose.dev.yml"
            fi
            ;;
        "prod"|"production")
            if [ -f "$PROJECT_ROOT/docker-compose.prod.yml" ]; then
                compose_files="$compose_files -f docker-compose.prod.yml"
            fi
            ;;
        "docker"|"")
            # Use base configuration only
            ;;
        *)
            print_error "Unknown environment: $env"
            exit 1
            ;;
    esac
    
    echo "$compose_files"
}

# Function to ensure Docker services are running
ensure_services_running() {
    local compose_config="$1"
    
    print_status "Checking Docker services..."
    
    cd "$PROJECT_ROOT"
    
    # Check if database service is running
    if ! docker-compose $compose_config ps database | grep -q "Up"; then
        print_warning "Database service is not running. Starting services..."
        docker-compose $compose_config up -d database
        
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if docker-compose $compose_config exec -T database mysqladmin ping -h localhost --silent; then
                print_status "Database is ready"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                print_error "Database failed to start within expected time"
                exit 1
            fi
            
            sleep 2
            ((attempt++))
        done
    else
        print_status "Database service is running"
    fi
}

# Function to setup backup environment
setup_backup_environment() {
    print_status "Setting up backup environment..."
    
    # Create backup directory
    local backup_dir="$PROJECT_ROOT/database/backups"
    mkdir -p "$backup_dir"
    
    # Set appropriate permissions
    chmod 755 "$backup_dir"
    
    # Create .gitkeep if it doesn't exist
    if [ ! -f "$backup_dir/.gitkeep" ]; then
        echo "# Database backups directory" > "$backup_dir/.gitkeep"
    fi
    
    print_status "Backup environment setup complete"
    print_status "Backup directory: $backup_dir"
}

# Parse command line arguments
COMMAND=""
ENVIRONMENT="docker"
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        backup|restore|list|cleanup|setup)
            COMMAND="$1"
            shift
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            if [ -z "$COMMAND" ]; then
                print_error "Unknown command: $1"
                show_usage
                exit 1
            else
                # This might be a file argument for restore command
                BACKUP_FILE="$1"
                shift
            fi
            ;;
    esac
done

# Check if command was provided
if [ -z "$COMMAND" ]; then
    print_error "No command specified"
    show_usage
    exit 1
fi

# Get Docker Compose configuration
COMPOSE_CONFIG=$(get_compose_config "$ENVIRONMENT")

# Execute command
case "$COMMAND" in
    "setup")
        setup_backup_environment
        ;;
    
    "backup")
        ensure_services_running "$COMPOSE_CONFIG"
        
        # Determine backup script arguments
        local backup_args=""
        if [ "$FORCE" = true ]; then
            backup_args="$backup_args --force"
        fi
        
        # Set database name based on environment
        case "$ENVIRONMENT" in
            "dev"|"development")
                backup_args="$backup_args -d clash_deck_builder_dev"
                ;;
            "prod"|"production")
                backup_args="$backup_args -d clash_deck_builder"
                ;;
            *)
                backup_args="$backup_args -d clash_deck_builder_docker"
                ;;
        esac
        
        print_status "Creating backup for $ENVIRONMENT environment..."
        "$SCRIPT_DIR/backup-database.sh" $backup_args
        ;;
    
    "restore")
        if [ -z "$BACKUP_FILE" ]; then
            print_error "No backup file specified for restore"
            "$SCRIPT_DIR/restore-database.sh" -l
            exit 1
        fi
        
        ensure_services_running "$COMPOSE_CONFIG"
        
        # Determine restore script arguments
        local restore_args=""
        if [ "$FORCE" = true ]; then
            restore_args="$restore_args -f"
        fi
        
        # Set database name based on environment
        case "$ENVIRONMENT" in
            "dev"|"development")
                restore_args="$restore_args -d clash_deck_builder_dev"
                ;;
            "prod"|"production")
                restore_args="$restore_args -d clash_deck_builder"
                ;;
            *)
                restore_args="$restore_args -d clash_deck_builder_docker"
                ;;
        esac
        
        print_status "Restoring backup for $ENVIRONMENT environment..."
        "$SCRIPT_DIR/restore-database.sh" $restore_args "$BACKUP_FILE"
        ;;
    
    "list")
        "$SCRIPT_DIR/restore-database.sh" -l
        ;;
    
    "cleanup")
        if [ -z "$BACKUP_FILE" ]; then
            print_error "No retention days specified for cleanup"
            echo "Usage: $0 cleanup DAYS"
            exit 1
        fi
        
        local retention_days="$BACKUP_FILE"  # BACKUP_FILE contains the days argument
        local backup_dir="$PROJECT_ROOT/database/backups"
        
        print_status "Cleaning up backups older than $retention_days days..."
        
        if [ "$retention_days" -gt 0 ]; then
            local old_backups=$(find "$backup_dir" -name "*_backup_*.sql*" -type f -mtime +$retention_days 2>/dev/null || true)
            
            if [ -n "$old_backups" ]; then
                echo "$old_backups" | while read -r old_backup; do
                    if [ -f "$old_backup" ]; then
                        print_status "Removing old backup: $(basename "$old_backup")"
                        rm -f "$old_backup"
                    fi
                done
                print_status "Cleanup completed"
            else
                print_status "No old backups found to clean up"
            fi
        else
            print_error "Invalid retention days: $retention_days"
            exit 1
        fi
        ;;
    
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

exit 0