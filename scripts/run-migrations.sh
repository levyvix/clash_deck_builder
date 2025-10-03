#!/bin/bash

# Script to run database migrations manually
# This can be used for troubleshooting or manual migration execution

set -e

echo "🔄 Manual Migration Runner"
echo "=========================="

# Default values
CONTAINER_NAME="clash-backend"
ENVIRONMENT="docker"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --container)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS] [COMMAND]"
            echo ""
            echo "Options:"
            echo "  --container NAME    Container name (default: clash-backend)"
            echo "  --env ENV          Environment (default: docker)"
            echo "  --help             Show this help message"
            echo ""
            echo "Commands:"
            echo "  migrate            Run pending migrations (default)"
            echo "  status             Show migration status"
            echo "  rollback VERSION   Rollback to specific version"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run migrations"
            echo "  $0 status                            # Check status"
            echo "  $0 rollback 20241203_120000         # Rollback"
            echo "  $0 --container my-backend migrate   # Custom container"
            exit 0
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Default command
COMMAND=${COMMAND:-migrate}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running or not accessible"
    exit 1
fi

# Check if container exists
if ! docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Container '${CONTAINER_NAME}' not found"
    echo "Available containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

# Check if container is running
if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "⚠️  Container '${CONTAINER_NAME}' is not running"
    echo "Starting container..."
    
    case $ENVIRONMENT in
        "development"|"dev")
            docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend
            ;;
        "production"|"prod")
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d backend
            ;;
        *)
            docker-compose up -d backend
            ;;
    esac
    
    echo "⏳ Waiting for container to be ready..."
    sleep 5
fi

# Execute migration command in container
echo "🚀 Executing migration command: $COMMAND"

case $COMMAND in
    "migrate")
        docker exec -it "$CONTAINER_NAME" python /app/database/migrations/container_migrate.py migrate
        ;;
    "status")
        docker exec -it "$CONTAINER_NAME" python /app/database/migrations/container_migrate.py status
        ;;
    "rollback")
        if [ -z "$2" ]; then
            echo "❌ Rollback requires a target version"
            echo "Usage: $0 rollback VERSION"
            exit 1
        fi
        docker exec -it "$CONTAINER_NAME" python /app/database/migrations/migrate.py rollback --target "$2" \
            --host database --port 3306 \
            --user "${DB_USER}" --password "${DB_PASSWORD}" --database "${DB_NAME}"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "Available commands: migrate, status, rollback"
        exit 1
        ;;
esac

echo "✅ Migration command completed successfully"