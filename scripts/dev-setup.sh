#!/bin/bash

# =============================================================================
# DEVELOPMENT SETUP SCRIPT
# =============================================================================
# This script helps set up different development environments for the
# Clash Royale Deck Builder application.
# =============================================================================

set -e

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists node; then
        missing_deps+=("node")
    fi
    
    if ! command_exists npm; then
        missing_deps+=("npm")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_error "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to set up environment files
setup_environment() {
    print_status "Setting up environment files..."
    
    # Run the main environment setup script
    if [ -f "./scripts/setup-env.sh" ]; then
        chmod +x ./scripts/setup-env.sh
        ./scripts/setup-env.sh
    else
        print_warning "Environment setup script not found, creating basic files..."
        
        # Create basic environment files if they don't exist
        if [ ! -f ".env.local" ] && [ -f ".env.example" ]; then
            cp .env.example .env.local
            print_status "Created .env.local from template"
        fi
        
        if [ ! -f ".env.docker" ] && [ -f ".env.example" ]; then
            cp .env.example .env.docker
            print_status "Created .env.docker from template"
        fi
    fi
    
    # Create frontend environment files
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
# Frontend environment configuration
REACT_APP_API_BASE_URL=http://localhost:8000
GENERATE_SOURCEMAP=true
BROWSER=none
PORT=3000
EOF
        print_status "Created frontend/.env"
    fi
    
    print_success "Environment files are ready"
}

# Function to install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    
    cd frontend
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
    cd ..
    
    print_success "Frontend dependencies installed"
}

# Function to start full containerized development
start_containerized() {
    print_status "Starting containerized development environment..."
    
    # Start backend and database containers
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are healthy
    if docker-compose ps | grep -q "Up (healthy)"; then
        print_success "Containerized backend and database are running"
        print_status "Backend API: http://localhost:8000"
        print_status "Database: localhost:3306"
        print_status ""
        print_status "To start the frontend:"
        print_status "  cd frontend && npm start"
        print_status ""
        print_status "To view logs:"
        print_status "  docker-compose logs -f backend"
        print_status "  docker-compose logs -f database"
    else
        print_error "Some services failed to start properly"
        docker-compose ps
        exit 1
    fi
}

# Function to start frontend only
start_frontend_only() {
    print_status "Starting frontend development server..."
    
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    print_success "Frontend started (PID: $FRONTEND_PID)"
    print_status "Frontend: http://localhost:3000"
    print_status "Make sure the backend is running on http://localhost:8000"
}

# Function to start backend only
start_backend_only() {
    print_status "Starting backend-only development..."
    
    # Start only database container
    docker-compose up -d database
    
    print_status "Database container started"
    print_status "To start the backend locally:"
    print_status "  cd backend"
    print_status "  uv install"
    print_status "  cp ../.env.local .env"
    print_status "  # Edit .env and set DB_HOST=localhost"
    print_status "  uv run uvicorn main:app --reload"
}

# Function to show status
show_status() {
    print_status "Development environment status:"
    print_status ""
    
    # Check Docker containers
    if docker-compose ps | grep -q "Up"; then
        print_status "Docker containers:"
        docker-compose ps
    else
        print_status "No Docker containers running"
    fi
    
    print_status ""
    
    # Check if frontend is running
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend is running on http://localhost:3000"
    else
        print_status "Frontend is not running"
    fi
    
    # Check if backend is running
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend is running on http://localhost:8000"
    else
        print_status "Backend is not running"
    fi
}

# Function to stop all services
stop_all() {
    print_status "Stopping all development services..."
    
    # Stop Docker containers
    docker-compose down
    
    # Kill any running frontend processes
    pkill -f "react-scripts start" || true
    
    print_success "All services stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up development environment..."
    
    # Stop and remove containers and volumes
    docker-compose down -v
    
    # Remove node_modules (optional)
    read -p "Remove frontend node_modules? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf frontend/node_modules
        print_status "Removed frontend/node_modules"
    fi
    
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Development Setup Script for Clash Royale Deck Builder"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup           Set up development environment (run this first)"
    echo "  containerized   Start full containerized development (recommended)"
    echo "  frontend        Start frontend development server only"
    echo "  backend         Start backend-only development (with containerized DB)"
    echo "  status          Show current development environment status"
    echo "  stop            Stop all development services"
    echo "  cleanup         Clean up development environment"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup           # Initial setup"
    echo "  $0 containerized   # Start full development environment"
    echo "  $0 frontend        # Start only frontend (backend must be running)"
    echo "  $0 status          # Check what's running"
    echo "  $0 stop            # Stop everything"
}

# Main script logic
case "${1:-help}" in
    setup)
        check_prerequisites
        setup_environment
        install_frontend_deps
        print_success "Development environment setup completed!"
        print_status "Run '$0 containerized' to start the full development environment"
        ;;
    containerized)
        check_prerequisites
        setup_environment
        start_containerized
        ;;
    frontend)
        check_prerequisites
        install_frontend_deps
        start_frontend_only
        ;;
    backend)
        check_prerequisites
        setup_environment
        start_backend_only
        ;;
    status)
        show_status
        ;;
    stop)
        stop_all
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac