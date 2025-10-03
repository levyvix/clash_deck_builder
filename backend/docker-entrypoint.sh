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
    
    # Change to migrations directory
    cd /app/database/migrations
    
    # Run migrations using the container-specific script
    if python container_migrate.py migrate; then
        echo "✅ Database migrations completed successfully"
    else
        echo "❌ Database migrations failed"
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
    
    # Run migrations
    run_migrations
    
    echo "🎉 Backend initialization completed successfully!"
    echo "🚀 Starting application server..."
    
    # Execute the main command passed to the container
    exec "$@"
}

# Handle signals gracefully
trap 'echo "⚠️  Received shutdown signal, stopping..."; exit 0' SIGTERM SIGINT

# Run main function with all arguments
main "$@"