#!/bin/bash
set -e

# Docker entrypoint script for backend container
# This script runs database migrations before starting the application

echo "🚀 Starting Clash Royale Deck Builder Backend..."

# Function to wait for database to be ready
wait_for_database() {
    echo "⏳ Waiting for database to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import mysql.connector
import os
import sys
try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'database'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    conn.close()
    print('✅ Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"; then
            echo "✅ Database is ready!"
            return 0
        fi
        
        echo "⏳ Database not ready yet (attempt $attempt/$max_attempts), waiting 2 seconds..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Database failed to become ready after $max_attempts attempts"
    exit 1
}

# Function to run database migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    
    # Set migration timeout from environment (default 5 minutes)
    local migration_timeout=${MIGRATION_TIMEOUT:-300}
    local migration_log_level=${MIGRATION_LOG_LEVEL:-info}
    
    # Create migration logs directory
    mkdir -p /app/database/migrations/logs
    
    # Generate log file with timestamp
    local log_file="/app/database/migrations/logs/migration_$(date +%Y%m%d_%H%M%S).log"
    
    echo "📝 Migration logs will be written to: $log_file"
    echo "⏱️  Migration timeout set to: ${migration_timeout}s"
    
    # Change to migrations directory
    cd /app/database/migrations
    
    # Run migrations with timeout and logging
    echo "🚀 Starting migration process..."
    
    # First check migration status
    echo "📊 Checking current migration status..."
    if timeout $migration_timeout python container_migrate.py status 2>&1 | tee -a "$log_file"; then
        echo "✅ Migration status check completed"
    else
        echo "⚠️  Migration status check failed, but continuing with migration attempt..."
    fi
    
    # Run the actual migrations
    echo "🔄 Executing pending migrations..."
    if timeout $migration_timeout python container_migrate.py migrate 2>&1 | tee -a "$log_file"; then
        echo "✅ Database migrations completed successfully"
        
        # Log final status
        echo "📊 Final migration status:" | tee -a "$log_file"
        python container_migrate.py status 2>&1 | tee -a "$log_file"
        
        # Create success marker file
        echo "$(date): Migration completed successfully" > /app/database/migrations/logs/last_migration_success
        
    else
        local exit_code=$?
        echo "❌ Database migrations failed with exit code: $exit_code" | tee -a "$log_file"
        
        # Create failure marker file
        echo "$(date): Migration failed with exit code $exit_code" > /app/database/migrations/logs/last_migration_failure
        
        # Log error details
        echo "💥 Migration failure details:" | tee -a "$log_file"
        echo "  - Exit code: $exit_code" | tee -a "$log_file"
        echo "  - Timestamp: $(date)" | tee -a "$log_file"
        echo "  - Log file: $log_file" | tee -a "$log_file"
        
        # Try to get final status for debugging
        echo "🔍 Attempting to get final migration status for debugging..." | tee -a "$log_file"
        python container_migrate.py status 2>&1 | tee -a "$log_file" || true
        
        exit 1
    fi
    
    # Return to app directory
    cd /app
}

# Function to validate environment variables
validate_environment() {
    echo "🔍 Validating environment variables..."
    
    local required_vars=("DB_HOST" "DB_USER" "DB_PASSWORD" "DB_NAME")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "❌ Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    echo "✅ Environment variables validated"
}

# Function to setup logging
setup_logging() {
    # Create logs directory if it doesn't exist
    mkdir -p /app/logs
    
    # Set log level based on environment
    export LOG_LEVEL=${LOG_LEVEL:-info}
    
    echo "📝 Logging configured (level: $LOG_LEVEL)"
}

# Main startup sequence
main() {
    echo "🏁 Starting backend initialization sequence..."
    
    # Validate environment
    validate_environment
    
    # Setup logging
    setup_logging
    
    # Wait for database
    wait_for_database
    
    # Skip migrations - handled by database initialization scripts
    echo "ℹ️  Skipping migrations (handled by database init scripts)"
    
    # Run card data ingestion
    echo "📥 Running card data ingestion..."
    if [ -f "/all_cards.json" ]; then
        if python src/scripts/ingest_cards.py; then
            echo "✅ Card data ingestion completed successfully"
        else
            echo "⚠️  Card data ingestion failed, but continuing startup..."
        fi
    else
        echo "⚠️  all_cards.json not found, skipping card ingestion"
    fi
    
    echo "🎉 Backend initialization completed successfully!"
    echo "🚀 Starting application server..."
    
    # Execute the main command passed to the container
    exec "$@"
}

# Handle signals gracefully
trap 'echo "⚠️  Received shutdown signal, stopping..."; exit 0' SIGTERM SIGINT

# Run main function with all arguments
main "$@"