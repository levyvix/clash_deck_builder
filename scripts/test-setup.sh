#!/bin/bash

# Test environment setup script
# This script sets up the test database containers and runs tests

set -e

echo "Setting up test environment..."

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Error: Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to wait for service to be healthy
wait_for_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $service_name to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.test.yml ps $service_name | grep -q "healthy"; then
            echo "$service_name is healthy!"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "Error: $service_name failed to become healthy after $max_attempts attempts"
    return 1
}

# Function to cleanup test environment
cleanup() {
    echo "Cleaning up test environment..."
    docker-compose -f docker-compose.test.yml down -v --remove-orphans
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Check Docker
check_docker

# Stop any existing test containers
echo "Stopping existing test containers..."
docker-compose -f docker-compose.test.yml down -v --remove-orphans

# Start test database
echo "Starting test database..."
docker-compose -f docker-compose.test.yml up -d test-database

# Wait for database to be healthy
wait_for_service test-database

# Run database tests
echo "Running database integration tests..."
cd backend

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Installing backend dependencies..."
    uv sync
fi

# Run tests with test environment
echo "Running tests..."
uv run pytest tests/integration/ -v --tb=short

echo "Test setup and execution completed successfully!"