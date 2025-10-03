#!/bin/bash

# Database Backup Script for Clash Royale Deck Builder
# Creates timestamped MySQL database dumps with compression

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/database/backups"
CONTAINER_NAME="clash-db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Default values
DB_NAME="clash_deck_builder_docker"
BACKUP_RETENTION_DAYS=30
COMPRESS=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --database NAME     Database name (default: clash_deck_builder_docker)"
    echo "  -c, --container NAME    Container name (default: clash-db)"
    echo "  -o, --output DIR        Output directory (default: database/backups)"
    echo "  -r, --retention DAYS    Backup retention in days (default: 30)"
    echo "  --no-compress          Don't compress the backup file"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Basic backup with defaults"
    echo "  $0 -d my_database -r 7              # Custom database, 7-day retention"
    echo "  $0 --no-compress                     # Backup without compression"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--database)
            DB_NAME="$2"
            shift 2
            ;;
        -c|--container)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -o|--output)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            BACKUP_RETENTION_DAYS="$2"
            shift 2
            ;;
        --no-compress)
            COMPRESS=false
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if Docker container is running
if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    print_error "Database container '$CONTAINER_NAME' is not running"
    print_status "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

# Generate backup filename
if [ "$COMPRESS" = true ]; then
    BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql.gz"
    TEMP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql"
else
    BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql"
fi

print_status "Starting database backup..."
print_status "Database: $DB_NAME"
print_status "Container: $CONTAINER_NAME"
print_status "Output: $BACKUP_FILE"

# Create database dump
print_status "Creating database dump..."
if docker exec "$CONTAINER_NAME" mysqldump \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --add-drop-database \
    --databases "$DB_NAME" > "$TEMP_FILE" 2>/dev/null; then
    
    # Compress if requested
    if [ "$COMPRESS" = true ]; then
        print_status "Compressing backup..."
        if gzip "$TEMP_FILE"; then
            print_status "Backup compressed successfully"
        else
            print_error "Failed to compress backup"
            mv "$TEMP_FILE" "$BACKUP_FILE"
        fi
    fi
    
    # Get backup file size
    if [ -f "$BACKUP_FILE" ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        print_status "Backup completed successfully"
        print_status "Backup size: $BACKUP_SIZE"
        print_status "Backup location: $BACKUP_FILE"
    else
        print_error "Backup file not found after creation"
        exit 1
    fi
else
    print_error "Failed to create database dump"
    # Clean up temp file if it exists
    [ -f "$TEMP_FILE" ] && rm -f "$TEMP_FILE"
    exit 1
fi

# Clean up old backups based on retention policy
if [ "$BACKUP_RETENTION_DAYS" -gt 0 ]; then
    print_status "Cleaning up backups older than $BACKUP_RETENTION_DAYS days..."
    
    # Find and delete old backup files
    OLD_BACKUPS=$(find "$BACKUP_DIR" -name "${DB_NAME}_backup_*.sql*" -type f -mtime +$BACKUP_RETENTION_DAYS 2>/dev/null || true)
    
    if [ -n "$OLD_BACKUPS" ]; then
        echo "$OLD_BACKUPS" | while read -r old_backup; do
            if [ -f "$old_backup" ]; then
                print_status "Removing old backup: $(basename "$old_backup")"
                rm -f "$old_backup"
            fi
        done
    else
        print_status "No old backups found to clean up"
    fi
fi

# Verify backup integrity
print_status "Verifying backup integrity..."
if [ "$COMPRESS" = true ]; then
    if gzip -t "$BACKUP_FILE" 2>/dev/null; then
        print_status "Backup file integrity verified"
    else
        print_error "Backup file appears to be corrupted"
        exit 1
    fi
else
    if [ -s "$BACKUP_FILE" ]; then
        print_status "Backup file integrity verified"
    else
        print_error "Backup file is empty or corrupted"
        exit 1
    fi
fi

print_status "Database backup completed successfully!"
print_status "Backup file: $BACKUP_FILE"

# List recent backups
print_status "Recent backups in $BACKUP_DIR:"
ls -lah "$BACKUP_DIR"/${DB_NAME}_backup_*.sql* 2>/dev/null | tail -5 || print_warning "No backup files found"

exit 0