#!/bin/bash

# Database Restore Script for Clash Royale Deck Builder
# Restores MySQL database from backup files with validation and rollback capabilities

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/database/backups"
CONTAINER_NAME="clash-db"

# Default values
DB_NAME="clash_deck_builder_docker"
BACKUP_FILE=""
FORCE_RESTORE=false
CREATE_ROLLBACK=true
VALIDATE_BEFORE_RESTORE=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_prompt() {
    echo -e "${BLUE}[PROMPT]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] BACKUP_FILE"
    echo ""
    echo "Arguments:"
    echo "  BACKUP_FILE            Path to backup file (.sql or .sql.gz)"
    echo ""
    echo "Options:"
    echo "  -d, --database NAME    Database name (default: clash_deck_builder_docker)"
    echo "  -c, --container NAME   Container name (default: clash-db)"
    echo "  -b, --backup-dir DIR   Backup directory (default: database/backups)"
    echo "  -f, --force           Skip confirmation prompts"
    echo "  --no-rollback         Don't create rollback backup before restore"
    echo "  --no-validate         Skip backup file validation"
    echo "  -l, --list            List available backup files"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 database/backups/clash_deck_builder_backup_20241203_120000.sql.gz"
    echo "  $0 -f --no-rollback backup.sql                    # Force restore without rollback"
    echo "  $0 -l                                             # List available backups"
    echo "  $0 -d my_database backup.sql                      # Restore to different database"
}

# Function to list available backups
list_backups() {
    print_status "Available backup files in $BACKUP_DIR:"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_warning "Backup directory does not exist: $BACKUP_DIR"
        return 1
    fi
    
    local backup_files=$(find "$BACKUP_DIR" -name "*.sql" -o -name "*.sql.gz" 2>/dev/null | sort -r)
    
    if [ -z "$backup_files" ]; then
        print_warning "No backup files found in $BACKUP_DIR"
        return 1
    fi
    
    echo "$backup_files" | while read -r backup_file; do
        if [ -f "$backup_file" ]; then
            local size=$(du -h "$backup_file" | cut -f1)
            local date=$(stat -c %y "$backup_file" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1 || date -r "$backup_file" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "Unknown")
            echo "  $(basename "$backup_file") ($size, $date)"
        fi
    done
}

# Function to validate backup file
validate_backup_file() {
    local file="$1"
    
    print_status "Validating backup file: $(basename "$file")"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        print_error "Backup file does not exist: $file"
        return 1
    fi
    
    # Check file size
    if [ ! -s "$file" ]; then
        print_error "Backup file is empty: $file"
        return 1
    fi
    
    # Validate compressed files
    if [[ "$file" == *.gz ]]; then
        if ! gzip -t "$file" 2>/dev/null; then
            print_error "Backup file is corrupted (gzip test failed): $file"
            return 1
        fi
        
        # Check if it contains SQL content
        if ! gzip -dc "$file" 2>/dev/null | head -10 | grep -q "CREATE\|INSERT\|DROP\|USE"; then
            print_error "Backup file does not appear to contain valid SQL: $file"
            return 1
        fi
    else
        # Validate uncompressed SQL files
        if ! head -10 "$file" | grep -q "CREATE\|INSERT\|DROP\|USE"; then
            print_error "Backup file does not appear to contain valid SQL: $file"
            return 1
        fi
    fi
    
    print_status "Backup file validation passed"
    return 0
}

# Function to create rollback backup
create_rollback_backup() {
    local rollback_file="$BACKUP_DIR/${DB_NAME}_rollback_$(date +"%Y%m%d_%H%M%S").sql.gz"
    
    print_status "Creating rollback backup: $(basename "$rollback_file")"
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Create rollback backup
    if docker exec "$CONTAINER_NAME" mysqldump \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --add-drop-database \
        --databases "$DB_NAME" 2>/dev/null | gzip > "$rollback_file"; then
        
        print_status "Rollback backup created: $(basename "$rollback_file")"
        echo "$rollback_file"
        return 0
    else
        print_error "Failed to create rollback backup"
        return 1
    fi
}

# Function to restore database
restore_database() {
    local backup_file="$1"
    
    print_status "Starting database restore..."
    print_status "Source: $(basename "$backup_file")"
    print_status "Target database: $DB_NAME"
    print_status "Container: $CONTAINER_NAME"
    
    # Prepare SQL command based on file type
    if [[ "$backup_file" == *.gz ]]; then
        print_status "Decompressing and restoring from compressed backup..."
        if gzip -dc "$backup_file" | docker exec -i "$CONTAINER_NAME" mysql; then
            print_status "Database restore completed successfully"
            return 0
        else
            print_error "Database restore failed"
            return 1
        fi
    else
        print_status "Restoring from uncompressed backup..."
        if docker exec -i "$CONTAINER_NAME" mysql < "$backup_file"; then
            print_status "Database restore completed successfully"
            return 0
        else
            print_error "Database restore failed"
            return 1
        fi
    fi
}

# Function to verify restore
verify_restore() {
    print_status "Verifying database restore..."
    
    # Check if database exists and has tables
    local table_count=$(docker exec "$CONTAINER_NAME" mysql -e "USE $DB_NAME; SHOW TABLES;" 2>/dev/null | wc -l)
    
    if [ "$table_count" -gt 1 ]; then  # More than 1 because of header line
        print_status "Database restore verification passed ($((table_count - 1)) tables found)"
        
        # Show table summary
        print_status "Restored tables:"
        docker exec "$CONTAINER_NAME" mysql -e "USE $DB_NAME; SHOW TABLES;" 2>/dev/null | tail -n +2 | while read -r table; do
            local row_count=$(docker exec "$CONTAINER_NAME" mysql -e "USE $DB_NAME; SELECT COUNT(*) FROM $table;" 2>/dev/null | tail -n +2)
            echo "  - $table ($row_count rows)"
        done
        
        return 0
    else
        print_error "Database restore verification failed (no tables found)"
        return 1
    fi
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
        -b|--backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -f|--force)
            FORCE_RESTORE=true
            shift
            ;;
        --no-rollback)
            CREATE_ROLLBACK=false
            shift
            ;;
        --no-validate)
            VALIDATE_BEFORE_RESTORE=false
            shift
            ;;
        -l|--list)
            list_backups
            exit 0
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
            else
                print_error "Multiple backup files specified"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if backup file was provided
if [ -z "$BACKUP_FILE" ]; then
    print_error "No backup file specified"
    echo ""
    list_backups
    echo ""
    show_usage
    exit 1
fi

# Convert relative path to absolute if needed
if [[ "$BACKUP_FILE" != /* ]]; then
    if [[ "$BACKUP_FILE" == */* ]]; then
        BACKUP_FILE="$PROJECT_ROOT/$BACKUP_FILE"
    else
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
    fi
fi

# Check if Docker container is running
if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    print_error "Database container '$CONTAINER_NAME' is not running"
    print_status "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

# Validate backup file if requested
if [ "$VALIDATE_BEFORE_RESTORE" = true ]; then
    if ! validate_backup_file "$BACKUP_FILE"; then
        exit 1
    fi
fi

# Show restore summary and get confirmation
echo ""
print_status "=== RESTORE SUMMARY ==="
print_status "Backup file: $(basename "$BACKUP_FILE")"
print_status "File size: $(du -h "$BACKUP_FILE" | cut -f1)"
print_status "Target database: $DB_NAME"
print_status "Container: $CONTAINER_NAME"
print_status "Create rollback: $CREATE_ROLLBACK"
echo ""

if [ "$FORCE_RESTORE" = false ]; then
    print_warning "This operation will REPLACE all data in the '$DB_NAME' database!"
    print_prompt "Are you sure you want to continue? (yes/no): "
    read -r confirmation
    
    if [[ "$confirmation" != "yes" && "$confirmation" != "y" ]]; then
        print_status "Restore operation cancelled"
        exit 0
    fi
fi

# Create rollback backup if requested
ROLLBACK_FILE=""
if [ "$CREATE_ROLLBACK" = true ]; then
    if ROLLBACK_FILE=$(create_rollback_backup); then
        print_status "Rollback backup available at: $(basename "$ROLLBACK_FILE")"
    else
        if [ "$FORCE_RESTORE" = false ]; then
            print_error "Failed to create rollback backup. Aborting restore."
            exit 1
        else
            print_warning "Failed to create rollback backup, but continuing due to --force flag"
        fi
    fi
fi

# Perform the restore
if restore_database "$BACKUP_FILE"; then
    # Verify the restore
    if verify_restore; then
        print_status "Database restore completed successfully!"
        
        if [ -n "$ROLLBACK_FILE" ]; then
            print_status "Rollback backup available at: $(basename "$ROLLBACK_FILE")"
            print_status "To rollback this restore, run:"
            print_status "  $0 \"$ROLLBACK_FILE\""
        fi
    else
        print_error "Database restore verification failed"
        
        if [ -n "$ROLLBACK_FILE" ]; then
            print_warning "Consider rolling back using: $0 \"$ROLLBACK_FILE\""
        fi
        exit 1
    fi
else
    print_error "Database restore failed"
    
    if [ -n "$ROLLBACK_FILE" ]; then
        print_warning "Consider rolling back using: $0 \"$ROLLBACK_FILE\""
    fi
    exit 1
fi

exit 0