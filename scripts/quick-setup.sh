#!/bin/bash
# =============================================================================
# Quick Setup Script for Clash Royale Deck Builder
# =============================================================================
# This script helps you get started quickly with the centralized environment
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  Clash Royale Deck Builder - Quick Setup"
    echo "=============================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_header

print_step "Step 1: Setting up environment configuration"

# Check if .env already exists
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    print_warning ".env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Keeping existing .env file"
    else
        cp "$PROJECT_ROOT/.env.template" "$PROJECT_ROOT/.env"
        print_success "Created new .env from template"
    fi
else
    cp "$PROJECT_ROOT/.env.template" "$PROJECT_ROOT/.env"
    print_success "Created .env from template"
fi

print_step "Step 2: Checking required tools"

# Check for Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

# Check for Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python not found. Please install Python 3.11+ from https://python.org/"
    exit 1
fi

# Check for UV
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    print_success "UV found: $UV_VERSION"
else
    print_warning "UV not found. Installing UV..."
    if command -v pip &> /dev/null; then
        pip install uv
        print_success "UV installed successfully"
    else
        print_error "Cannot install UV. Please install it manually: https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# Check for MySQL
if command -v mysql &> /dev/null; then
    print_success "MySQL client found"
else
    print_warning "MySQL client not found. You may need to install MySQL or use Docker"
fi

print_step "Step 3: Installing dependencies"

# Install backend dependencies
print_info "Installing backend dependencies..."
cd "$PROJECT_ROOT/backend"
if uv install; then
    print_success "Backend dependencies installed"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi

# Install frontend dependencies
print_info "Installing frontend dependencies..."
cd "$PROJECT_ROOT/frontend"
if npm install; then
    print_success "Frontend dependencies installed"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

cd "$PROJECT_ROOT"

print_step "Step 4: Configuration guidance"

echo
print_info "Next steps to complete setup:"
echo
echo "1. 📝 Edit your .env file with actual values:"
echo "   - Database credentials (DB_PASSWORD, DB_ROOT_PASSWORD)"
echo "   - Google OAuth credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)"
echo "   - Clash Royale API key (CLASH_ROYALE_API_KEY)"
echo "   - JWT secret (JWT_SECRET_KEY - generate a secure 32+ character string)"
echo
echo "2. 🗄️  Set up your database:"
echo "   - Install MySQL locally, or"
echo "   - Use Docker: docker-compose up database"
echo
echo "3. 🔑 Get your API keys:"
echo "   - Google OAuth: https://console.cloud.google.com/"
echo "   - Clash Royale API: https://developer.clashroyale.com/"
echo
echo "4. ✅ Validate your configuration:"
echo "   source scripts/load-env.sh --validate"
echo
echo "5. 🚀 Start development:"
echo "   Backend:  cd backend && uv run uvicorn main:app --reload"
echo "   Frontend: cd frontend && npm start"
echo

print_info "For detailed setup instructions, see: ENVIRONMENT_SETUP.md"

print_success "Quick setup completed! 🎉"

echo
print_info "Useful commands:"
echo "  Load environment:    source scripts/load-env.sh"
echo "  Validate config:     source scripts/load-env.sh --validate"
echo "  Migrate old files:   python scripts/migrate-env.py"
echo "  Full setup guide:    cat ENVIRONMENT_SETUP.md"